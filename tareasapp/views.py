
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .models import Tarea


# ==========================================
# VISTAS HTML
# ==========================================

# Listar tareas
def inicio(request):
    tareas = Tarea.objects.all()

    return render(request, 'tareasapp/inicio.html', {
        'tareas': tareas
    })


# Crear tarea
def crear_tarea(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '')
        descripcion = request.POST.get('descripcion', '')
        completada = 'completa' in request.POST

        Tarea.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            completada=completada
        )

        return redirect('inicio')

    return render(request, 'tareasapp/crear.html')


# Ver detalle
def detalle_tarea(request, id):
    tarea = get_object_or_404(Tarea, id=id)

    return render(request, 'tareasapp/detalle.html', {
        'tarea': tarea
    })


# Editar tarea
def editar_tarea(request, id):
    tarea = get_object_or_404(Tarea, id=id)

    if request.method == 'POST':
        tarea.titulo = request.POST.get('titulo', '')
        tarea.descripcion = request.POST.get('descripcion', '')
        tarea.completada = 'completada' in request.POST

        tarea.save()

        return redirect('inicio')

    return render(request, 'tareasapp/editar.html', {
        'tarea': tarea
    })


# Eliminar tarea mediante formulario HTML tradicional
def eliminar_tarea(request, id):
    tarea = get_object_or_404(Tarea, id=id)

    if request.method == 'POST':
        tarea.delete()
        return redirect('inicio')

    return render(request, 'tareasapp/eliminar.html', {
        'tarea': tarea
    })


# Página de inicio de sesión
def login_pagina(request):
    return render(request, 'tareasapp/login.html')


# ==========================================
# API REST: INICIO DE SESIÓN
# ==========================================

class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        usuario = authenticate(
            username=username,
            password=password
        )

        if usuario is not None:
            token, creado = Token.objects.get_or_create(
                user=usuario
            )

            return Response({
                'mensaje': 'Autenticación correcta',
                'usuario': usuario.username,
                'token': token.key
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Usuario o contraseña incorrecta'
        }, status=status.HTTP_401_UNAUTHORIZED)


# ==========================================
# API REST: LISTAR TODAS LAS TAREAS
# ==========================================

class Tareasapiview(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tareas = Tarea.objects.all()

        datos = []

        for tarea in tareas:
            datos.append({
                'id': tarea.id,
                'titulo': tarea.titulo,
                'descripcion': tarea.descripcion,
                'completada': tarea.completada
            })

        return Response(datos, status=status.HTTP_200_OK)


# ==========================================
# API REST: CONSULTAR Y ELIMINAR UNA TAREA
# ==========================================



class TareaDetalleAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            return Tarea.objects.get(id=id)
        except Tarea.DoesNotExist:
            return None

    # GET: consultar una tarea
    def get(self, request, id):
        tarea = self.get_object(id)

        if tarea is None:
            return Response(
                {'error': 'Tarea no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'id': tarea.id,
            'titulo': tarea.titulo,
            'descripcion': tarea.descripcion,
            'completada': tarea.completada
        }, status=status.HTTP_200_OK)

    # PUT: reemplazar los datos de la tarea
    def put(self, request, id):
        tarea = self.get_object(id)

        if tarea is None:
            return Response(
                {'error': 'Tarea no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        campos = ['titulo', 'descripcion', 'completada']

        for campo in campos:
            if campo not in request.data:
                return Response(
                    {'error': f'Falta el campo {campo}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        resultado = self.actualizar_tarea(tarea, request.data)

        if resultado is not None:
            return resultado

        return self.respuesta_tarea(tarea)

    # PATCH: actualizar solo los campos enviados
    def patch(self, request, id):
        tarea = self.get_object(id)

        if tarea is None:
            return Response(
                {'error': 'Tarea no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        resultado = self.actualizar_tarea(tarea, request.data)

        if resultado is not None:
            return resultado

        return self.respuesta_tarea(tarea)

    # Validar y guardar los campos recibidos
    def actualizar_tarea(self, tarea, datos):
        campos_permitidos = {'titulo', 'descripcion', 'completada'}

        campos_recibidos = set(datos.keys())
        campos_invalidos = campos_recibidos - campos_permitidos

        if campos_invalidos:
            return Response(
                {'error': 'Hay campos no permitidos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not campos_recibidos:
            return Response(
                {'error': 'Debes enviar al menos un campo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'titulo' in datos:
            if not isinstance(datos['titulo'], str):
                return Response(
                    {'error': 'El título debe ser texto'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            tarea.titulo = datos['titulo']

        if 'descripcion' in datos:
            if not isinstance(datos['descripcion'], str):
                return Response(
                    {'error': 'La descripción debe ser texto'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            tarea.descripcion = datos['descripcion']

        if 'completada' in datos:
            valor = datos['completada']

            if not isinstance(valor, bool):
                return Response(
                    {'error': 'Completada debe ser true o false'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            tarea.completada = valor

        tarea.save()
        return None

    # Preparar la respuesta de la tarea
    def respuesta_tarea(self, tarea):
        return Response({
            'mensaje': 'Tarea actualizada correctamente',
            'id': tarea.id,
            'titulo': tarea.titulo,
            'descripcion': tarea.descripcion,
            'completada': tarea.completada
        }, status=status.HTTP_200_OK)

    # DELETE: eliminar una tarea
    def delete(self, request, id):
        tarea = self.get_object(id)

        if tarea is None:
            return Response(
                {'error': 'Tarea no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        tarea.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

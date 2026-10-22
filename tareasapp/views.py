from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Tarea
# Create your views here.

# def inicio(request):
#     return HttpResponse("Hola, esta es mi App de Tareas")

def inicio(request):
    tareas = Tarea.objects.all()

    return render(request, 'tareasapp/inicio.html') 


def crear_tarea(request):
    if request.method == 'POST':
        titulo = request.POST['titulo']
        descripcion = request.POST['descripcion']
        completada = 'completa'in request.POST

        Tarea.objects.create(
            titulo = titulo,
            descripcion = descripcion,
            completada = completada
        )
        return redirect('inicio')
    return render (request, 'tareasapp/crear.html')


def detalle_tarea(request, id):
    tarea = Tarea.objects.get(id=id)

    return render(request, 'tareasapp/detalle.html', {
        'tarea': tarea
    })


def editar_tarea(request, id):
    tarea = Tarea.objects.get(id=id)

    if request.method == 'POST':
        tarea.titulo = request.POST['titulo']
        tarea.descripcion = request.POST['descripcion']
        tarea.completada = 'completada' in request.POST

        tarea.save()
        return redirect('inicio')
    
    return render(request, 'tareasapp/editar.html', {
        'tarea': tarea
    })

def eliminar_tarea(request, id):
    tarea = Tarea.objects.get(id=id)

    if request.method == 'POST':
        tarea.delete()

        return redirect('inicio')
    
    return render(request, 'tareasapp/eliminar.html', {
        'tarea': tarea
    })

def login_pagina(request):
    return render(request, 'tareasapp/login.html')

class LoginAPIView(APIView):

    permission_classes =[AllowAny]

    def post(self, request):

        #Recibir las credenciales desde el JSON
        username = request.data.get('username')
        password = request.data.get('password')

        #Validar las credenciales de usuarios

        usuario = authenticate(
            username=username,
            password=password
        )

        if usuario is not None:

            token, creado = Token.objects.get_or_create(
                user=usuario
            )

            return Response({
                'mensaje': 'Autenticacion correcta',
                'usuario': usuario.username,
                'token':token.key
            }, status=status.HTTP_200_OK)
        return Response({
            'error': 'Usuario o contraseña incorrecta'
        }, status=status.HTTP_401_UNAUTHORIZED)

class Tareasapiview(APIView):
    authentication_clasess = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #GET LISTAR todas las tareas
    def get(self, request):
        tareas = Tarea.objects.all()
        datos = []

        for tarea in tareas:
            datos.append({
                'id': tarea.id,  
                'titulo':tarea.titulo,   
                'descripcion':tarea.descripcion,
                'completada':tarea.completada
            })
        return Response(datos, status.HTTP_200_OK)
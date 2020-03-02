from django.contrib.auth import login, logout, authenticate, update_session_auth_hash

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from user.models import SluglineUser, UserSerializer


class IsEditor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_editor or request.user.is_staff))


class SluglineAPIException(APIException):
    def __init__(self, detail):
        super().__init__(detail={
            'success': False,
            'error': [detail] if isinstance(detail, str) else detail
        })


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if username is None or password is None:
        raise SluglineAPIException('AUTH.CREDENTIALS_NONEXISTENT')
    user = authenticate(username=username, password=password)
    if user is None:
        raise SluglineAPIException('AUTH.CREDENTIALS_INVALID')
    login(request, user)
    return Response(UserSerializer(user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response()


@api_view(['GET'])
def auth_view(request):
    if request.user is None or not request.user.is_authenticated:
        return Response({
            'authenticated': False
        })
    else:
        return Response({
            'authenticated': True,
            'user': UserSerializer(request.user).data
        })


@api_view(['GET'])
@permission_classes([IsEditor])
def list_users_view(request):
    start = int(request.GET.get('start', 0))
    limit = int(request.GET.get('limit', 10))
    return Response(map(lambda u: UserSerializer(u).data, SluglineUser.objects.all()[start:start+limit]))


@api_view(['GET'])
@permission_classes([IsEditor])
def list_user_view(request, username):
    try:
        return Response(UserSerializer(SluglineUser.objects.get(username=username)).data)
    except SluglineUser.DoesNotExist:
        raise SluglineAPIException('USER.DOES_NOT_EXIST')


@api_view(['PUT'])
@permission_classes([IsEditor])
def create_user_view(request, username):
    if SluglineUser.objects.filter(username=username).exists():
        return Response({
            'success': False,
            # NOTE: do we really need to return the user?
            'user': UserSerializer(SluglineUser.objects.get(username=username)).data
        })

    request.data['username'] = username
    serializer = UserSerializer(data=request.data)
    serializer.is_valid()
    if len(serializer.errors):
        raise SluglineAPIException(serializer.errors)
    else:
        try:
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data={
                'success': True,
                'user': serializer.data
            })
        except Exception:
            raise SluglineAPIException('USER.COULD_NOT_CREATE')


def update_user(user, request):
    data = request.data
    if 'new_password' in data:
        password = data.get('cur_password', '')
        if not user.check_password(password):
            raise SluglineAPIException({'user': ['USER.PASSWORD.CURRENT_INCORRECT']})
        if 'repeat_password' not in data or data['new_password'] != data['repeat_password']:
            raise SluglineAPIException({'user': ['USER.PASSWORD.MUST_MATCH']})
        data['password'] = data['new_password']
        del data['cur_password']
        del data['new_password']
        del data['repeat_password']

    # We set the partial flag as the front-end may not choose to update all fields at once
    serializer = UserSerializer(data=data, instance=user, partial=True)
    serializer.is_valid()
    if len(serializer.errors):
        raise SluglineAPIException(serializer.errors)
    else:
        try:
            updated_user = serializer.save()
            if 'password' in data:
                update_session_auth_hash(request, updated_user)
            return Response({
                'success': True,
                'user': serializer.data
            })
        except Exception:
            raise SluglineAPIException('USER.COULD_NOT_UPDATE')


@api_view(['POST'])
@permission_classes([IsEditor])
def update_generic_user_view(request, username):
    try:
        return update_user(user=SluglineUser.objects.get(username=username), request=request)
    except SluglineUser.DoesNotExist:
        raise SluglineAPIException('USER.DOES_NOT_EXIST')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_view(request):
    if not request.user.is_staff and not request.user.is_editor and any(['is_editor' in request.data]):
        raise SluglineAPIException('USER.INSUFFICIENT_PRIVILEGES')
    return update_user(user=request.user, request=request)


@api_view(['DELETE'])
@permission_classes([IsEditor])
def delete_user_view(request, username):
    try:
        SluglineUser.objects.filter(username=username).delete()
        return Response({
            'success': True
        })
    except SluglineUser.DoesNotExist:
        raise SluglineAPIException('USER.DOES_NOT_EXIST')
    except Exception:
        raise SluglineAPIException('USER.COULD_NOT_DELETE')

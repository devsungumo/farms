from rest_framework import status
from rest_framework.response import Response


class ApiResponse:
    @staticmethod
    def success(data=None, status_code=status.HTTP_200_OK):
        return Response({'success': True, 'data': data}, status=status_code)

    @staticmethod
    def created(data=None):
        return Response({'success': True, 'data': data}, status=status.HTTP_201_CREATED)

    @staticmethod
    def error(error, message, status_code=status.HTTP_400_BAD_REQUEST, details=None):
        payload = {'success': False, 'error': error, 'message': message}
        if details:
            payload['details'] = details
        return Response(payload, status=status_code)

    @staticmethod
    def not_found(message='Resource not found.'):
        return Response(
            {'success': False, 'error': 'not_found', 'message': message},
            status=status.HTTP_404_NOT_FOUND,
        )

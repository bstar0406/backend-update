import json

from rest_framework.permissions import BasePermission


class IsAuthorized(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        permissions_dict = self.load_permissions()
        user_persona = {request.user.persona}
        permissions_personas = permissions_dict.keys()
        persona_found = user_persona.intersection(permissions_personas)

        if not persona_found:
            return False

        persona_endpoints = permissions_dict[persona_found]

        for endpoint in persona_endpoints:
            if request.path == endpoint or (":id" in endpoint and endpoint[:-4] in request.path):
                method_permissions = persona_endpoints[endpoint]
                if request.method.upper() in method_permissions:
                    return method_permissions[request.method]

        return False

    def load_permissions(self) -> dict:
        with open('core/permissions.json', 'r+') as permissions_file:
            permisisons_dict = json.load(permissions_file)
        return permisisons_dict

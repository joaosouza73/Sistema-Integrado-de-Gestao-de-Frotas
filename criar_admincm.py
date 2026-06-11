from datetime import UTC, datetime

from dotenv import load_dotenv

from firebase_service import create_document, find_one

load_dotenv()

ADMIN_EMAIL = "admincm@admin.com"


def main():
    existente = find_one("usuarios", "email", ADMIN_EMAIL)

    admin = {
        "nome": "admincm",
        "email": ADMIN_EMAIL,
        "cargo": "Administrador",
        "departamento": "Administração",
        "perfil": "admin",
        "criado_em": datetime.now(UTC),
    }

    if existente:
        create_document("usuarios", admin, document_id=existente["_id"])
        print(f"Admin atualizado: {ADMIN_EMAIL}")
        return

    create_document("usuarios", admin, document_id="admincm")
    print(f"Admin criado: {ADMIN_EMAIL}")


if __name__ == "__main__":
    main()

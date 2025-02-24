from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from models import models
from app.security import get_current_employee

def require_role(required_role: str):
    """
    Dependency function to enforce role-based access control (RBAC).

    Args:
        required_role (str): The minimum role required to access a resource.

    Returns:
        Callable: A dependency function that checks the current employee's role.

    Raises:
        HTTPException: If the employee does not have the required permissions.
    """
    def role_dependency(current_employee: models.Employee = Depends(get_current_employee)):
        """
        Validates if the current employee has the required role.

        Args:
            current_employee (models.Employee): The authenticated employee.

        Returns:
            models.Employee: The authenticated employee if they have the required permissions.

        Raises:
            HTTPException: If the employee lacks the necessary role.
        """
        role_hierarchy = {"admin": 3, "manager": 2, "teller": 1}

        if role_hierarchy.get(current_employee.role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(status_code = 403, detail = "Permission denied")

        return current_employee
    return role_dependency
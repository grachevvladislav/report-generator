from asgiref.sync import sync_to_async
from bot.constants.states import States
from core.models import BotRequest, Employee
from salary.models import HourlyPayment


async def get_employee(update):
    """Get employee or make request."""
    try:
        employee = await Employee.objects.aget(
            telegram_id=update.effective_chat["id"], is_active=True
        )
    except Employee.DoesNotExist:
        try:
            await BotRequest.objects.aget(telegram_id=update.effective_chat.id)
        except BotRequest.DoesNotExist:
            await BotRequest.objects.acreate(
                telegram_id=update.effective_chat.id,
                first_name=update.effective_chat.first_name,
                last_name=update.effective_chat.last_name,
                username=update.effective_chat.username,
            )
        return None
    return employee


async def has_schedule_permission(employee):
    """
    Check user permission for schedule.

    :return: (is_admitted, employee_filter)
    """
    if employee.is_stuff or employee.is_owner:
        return True, None
    has_hourly_payment = sync_to_async(
        HourlyPayment.objects.filter(
            contract__сontract__employee=employee.id
        ).exists
    )()
    if await has_hourly_payment:
        return True, employee
    return False, None


async def get_permission(update) -> dict:
    """
    Check all permissions.

    Returns a dictionary with the names of sections and the rights in them.
    """
    employee = await get_employee(update)
    if not employee:
        return {}
    return {
        States.SCHEDULE: await has_schedule_permission(employee),
    }

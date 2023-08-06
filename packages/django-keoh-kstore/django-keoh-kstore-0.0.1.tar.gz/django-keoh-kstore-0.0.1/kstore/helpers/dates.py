from datetime import date, timedelta

def get_week(day):
    '''
        Dado un dia, devuelve un array con la fecha del lunes de esa
        semana y del domingo
    '''
    day_offset = 6 - day.weekday()
    lunes = day - timedelta(days=day.weekday())
    domingo = day + timedelta(days=day_offset)
    return [lunes, domingo]

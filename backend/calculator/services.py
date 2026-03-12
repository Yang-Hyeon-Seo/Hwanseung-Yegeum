from decimal import Decimal, ROUND_DOWN

def f_days_period(start_date, end_date):
    """
    하루단위 기간 계산
    input : 시작 날짜, 끝 날짜
    """
    return (end_date - start_date).days

def f_quantize(value):
    return int(value.quantize(Decimal('1E1'), rounding=ROUND_DOWN))

def f_interest(committed_amount, interest_rate, period, year):
    """
    세전이자 계산
    input : 원금, 이자율, 실제일수, 1년 일 수
    """
    interest =  committed_amount * interest_rate * period / year
    return f_quantize(interest)
    
def f_tax(interest, tax_rate):
    """
    세후 이자 계산
    input : 이자, 세율
    """
    tax_amount = f_quantize(interest * tax_rate)
    return interest - tax_amount

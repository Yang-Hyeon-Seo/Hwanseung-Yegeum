def f_maturity_calculate(committed_amount, contract_period, interest_rate, tax_rate):
    """
    만기 시 이자 계산
    input : 약정 금액, 약정 기간(연단위), 이자율(소수점단위), 이자소득세
    output : 만기 시 이자
    """
    interest = committed_amount * interest_rate * contract_period
    tax = interest * tax_rate
    return interest - tax

def f_early_calculate(committed_amount, subscription_period, interest_rate, tax_rate, year):
    """
    중도 해지 시 이자 계산
    input: 약정 금액, 가입 일수(하루단위), 중도 해지 이자율(소수점단위), 이자소득세, 1년 길이(일반 - 365, 윤년 - 366)
    """
    
    interest = committed_amount * interest_rate * subscription_period / year
    tax = interest * tax_rate
    return interest - tax

def f_new_interest(
        tax_rate,
        today,
        year,
        original_amount, 
        original_end_date,
        original_start_date,
        original_stop_rate,
        new_amount, 
        new_end_date,
        new_interest_rate
        ):
    
    # 1-1 중도해지
    print('중도해지')
    print(
        original_amount, 
        original_end_date-original_start_date,
        original_stop_rate,
        tax_rate,
        year
        )
    
    # 중도 해지 이자
    early_interest = f_early_calculate(
        original_amount, 
        original_end_date-original_start_date,
        original_stop_rate,
        tax_rate,
        year
        )
    
    # 1-2 신규 예금 만기 이자율 계산
    print('신규 예금')
    print(
        original_amount + early_interest, 
        (new_end_date - today).days / year,
        new_interest_rate,
        tax_rate
        )
    
    new_interest = f_maturity_calculate(
        new_amount, 
        (new_end_date - today).days / year,
        new_interest_rate,
        tax_rate
        )
    
    return early_interest + new_interest

def f_accumulated_interest(committed_amount, subscription_period, interest_rate, tax_rate, year):
    """
    만기 보유 가정, 지금까지 모은 금액
    input : 약정 금액, 가입 일수(하루단위), 이자율(소수점단위), 이자소득세, 1년 길이
    """
    original_interest = f_maturity_calculate(committed_amount, 1, interest_rate, tax_rate) # 이자율에 대한 하루치 이자 계산 -> 기간 1로 잡으면 됨
    interest_per_days = original_interest / year
    return interest_per_days * subscription_period
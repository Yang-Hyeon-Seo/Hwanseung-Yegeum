from django.shortcuts import render
from .services import f_days_period, f_interest, f_tax
from django.conf import settings

import json

from rest_framework.decorators import api_view
from rest_framework.response import Response

from datetime import datetime
import calendar
from decimal import Decimal
# Create your views here.

@api_view(['POST'])
def hwanseung_yegeum(request):
    """
    - 해지 및 가입 날짜
    - 기존 예금의 
      - 약정 금액
      - 가입일
      - 만기일
      - 이자율
      - 해당 날짜 기준 중도 해지 이자
    - 새 예금의 
      - 만기일
      - 이자율
        (새 예금의 약정 금액은 기존 예금 + 기존 예금의 만기 해지 이자)
    """
    tax_rate = Decimal(str(settings.TAX_RATE))
    year = Decimal('365')

    data = json.loads(request.body)
    
    # 해지 및 가입 날짜(조회 날짜) - 사용자 선택 가능
    today = data.get('today')
    today = datetime.strptime(today, "%Y-%m-%d").date()  # 날짜 객체로 변환
    
    # 기존 예금
    original_amount = Decimal(str(data.get('committed_amount')))
    original_start_date = data.get('original_start_date')
    original_start_date = datetime.strptime(original_start_date, '%Y-%m-%d').date()
    original_end_date = data.get('original_end_date')
    original_end_date = datetime.strptime(original_end_date, '%Y-%m-%d').date()
    original_interest_rate = Decimal(str(data.get('original_interest_rate') * 0.01))
    
    # 세후 중도 해지 이자
    early_termination_interest = Decimal(str(data.get('early_termination_interest')))

    # 신규 예금
    # new_amount = data.get('new_amount')
    new_end_date = data.get('new_end_date')
    new_end_date = datetime.strptime(new_end_date, '%Y-%m-%d').date()
    new_interest_rate = Decimal(str(data.get('new_interest_rate') * 0.01))
    
    # 1. 신규 예금 만기 이자 계산 
    print('중도 해지')
    # 1-1 세후 중도 해지 이자
    # 1-2 세전 신규 예금 만기 이자
    new_period = f_days_period(today, new_end_date)
    new_interest_before_tax = f_interest(
        original_amount + early_termination_interest,
        new_interest_rate,
        new_period,
        year
        )
    print("세전 신규 예금 만기 이자 :", new_interest_before_tax)
    # 1-3 세후 신규 예금 만기 이자
    new_interest = f_tax(new_interest_before_tax, tax_rate)
    print("세후 신규 예금 만기 이자 :", new_interest)


    # 2. 기존 예금 유지
    print('기존 예금 유지')
    # 세전 이자
    original_period = f_days_period(original_start_date, original_end_date)
    original_interest_before_tax = f_interest(
        original_amount, 
        original_interest_rate, 
        original_period,
        year
        )
    print('기존 예금 세전 만기 이자 :', original_interest_before_tax)
    # 세후 이자
    original_interest = f_tax(original_interest_before_tax, tax_rate)
    print('기존 예금 세후 만기 이자 :', original_interest)

    # 3. 스트레스 테스트
    additional_period = f_days_period(original_end_date, new_end_date)
    # 3-1 금리 유지(최신 상품 기준)
    # 세전이자
    maintain_interest_before_tax = f_interest(
        original_amount + original_interest,
        new_interest_rate,
        additional_period,
        year
    )
    # 세후이자
    maintain_interest = f_tax(maintain_interest_before_tax, tax_rate)
    print('금리 유지 시 이자율 :', new_interest_rate)
    print('금리 유지 시 세전 이자 :', maintain_interest_before_tax)
    print('금리 유지 시 세후 이자 :', maintain_interest)

    # 3-2 금리 인상(0.25%)
    # 세전이자
    increased_interest_before_tax = f_interest(
        original_amount + original_interest,
        new_interest_rate + Decimal('0.0025'),
        additional_period,
        year
    )
    # 세후이자
    increased_interest = f_tax(increased_interest_before_tax, tax_rate)
    print('금리 인상 시 이자율 :', new_interest_rate)
    print('금리 인상 시 세전 이자 :', increased_interest_before_tax)
    print('금리 인상 시 세후 이자 :', increased_interest)

    # 3-3 금리 인하(-0.25%)
    # 세전이자
    decreased_interest_before_tax = f_interest(
        original_amount + original_interest,
        new_interest_rate - Decimal('0.0025'),
        additional_period,
        year
    )
    # 세후이자
    decreased_interest = f_tax(decreased_interest_before_tax, tax_rate)
    print('금리 하락 시 이자율 :', new_interest_rate)
    print('금리 하락 시 세전 이자 :', decreased_interest_before_tax)
    print('금리 하락 시 세후 이자 :', decreased_interest)

    # 3-4 직접 결정

    # 결과
    result = {
        "original" : {
            "maintain" : {
                "total" : original_amount + original_interest + maintain_interest,
                "interest" : original_interest + maintain_interest,  # 세후이자
                },
            "increase" : {
                "total" : original_amount + original_interest + increased_interest,
                "interest" : original_interest + increased_interest,
                },
            "decrease" : {
                "total" : original_amount + original_interest + decreased_interest,
                "interest" : original_interest + decreased_interest,
                },
            },
        "hwanseung" : {
            "total" : original_amount + new_interest,
            "interest" : new_interest,
        },
    }
    return Response(result, status=200)
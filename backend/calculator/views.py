from django.shortcuts import render
from services import f_maturity_calculate, f_accumulated_interest, f_new_interest
from django.conf import settings

import json

from rest_framework.decorators import api_view
from rest_framework.response import Response

from datetime import datetime
import calendar
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
      - 중도 해지 이자율(소수점단위)
    - 새 예금의 
      - 만기일
      - 이자율
        (새 예금의 약정 금액은 기존 예금 + 기존 예금의 만기 해지 이자)
    """
    tax_rate = settings.TAX_RATE
    
    data = json.load(request.body)
    
    # 해지 및 가입 날짜(조회 날짜) - 사용자 선택 가능
    today = data.get('today')
    today = datetime.strftime(today, "%Y-%m-%d").date()  # 날짜 객체로 변환
    
    # 기존 예금
    original_amount = data.get('committed_amount')
    original_start_date = data.get('original_start_date')
    original_start_date = datetime.strftime(original_start_date, '%Y-%m-%d').date()
    original_end_date = data.get('original_end_date')
    original_end_date = datetime.strftime(original_end_date, '%Y-%m-%d').date()
    original_interest_rate = data.get('original_interest_date') * 0.01
    original_stop_rate = data.get('original_stop_date')

    # 기존에 가입한 상품이 윤년에 해당하는지 여부
    is_leap = calendar.isleap(original_start_date.year)
    if is_leap:
        year = 366  # 윤년
    else:
        year = 365

    # 신규 예금
    new_amount = data.get('new_amount')
    new_end_date = data.get('new_end_date')
    new_end_date = datetime.strftime(new_end_date, '%Y-%m-%d').date()
    new_interest_rate = data.get('new_interest_rate') * 0.01
    
    # 1. 신규 예금 만기 이자율 계산 
    new_interest = f_new_interest(
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
    )

    # 2. 기존 예금 유지
    original_interest = f_maturity_calculate(
        original_amount,
        (original_end_date - original_start_date).days / year,
        original_interest_rate,
        tax_rate
    )

    # 3. 스트레스 테스트
    # 3-1 금리 유지(최신 상품 기준)
    maintain_interest = f_accumulated_interest(
        original_amount + original_interest, 
        (new_end_date - original_end_date).days,
        new_interest_rate,
        tax_rate,
        year
        )
    # 3-2 금리 인상(0.25%)
    increased_interest = f_accumulated_interest(
        original_amount + original_interest, 
        (new_end_date - original_end_date).days,
        new_interest_rate + 0.0025,
        tax_rate,
        year
        )
    # 3-3 금리 인하(-0.25%)
    decreased_interest = f_accumulated_interest(
        original_amount + original_interest, 
        (new_end_date - original_end_date).days,
        new_interest_rate - 0.0025,
        tax_rate,
        year
        )
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
                "interest" : original_interest + decreased_interest
                },
            },
        "hwanseung" : {
            "total" : original_amount + new_interest,
            "interest" : new_interest,
        },
    }
    return Response(result, status=200)
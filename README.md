# CPU 스케줄러 시뮬레이터

---

## **1. 목적**

이 프로그램은 CPU 스케줄링 알고리즘을 시뮬레이션하여 사용자에게 다음과 같은 도움을 제공합니다:
- CPU 스케줄링 알고리즘의 동작 원리 이해.
- 다양한 알고리즘의 성능을 주요 지표를 기반으로 비교:
  - **평균 대기 시간 (Average Waiting Time).**
  - **평균 반환 시간 (Average Turnaround Time).**
  - **문맥 전환 횟수 (Context Switches).**
  - **CPU 활용도 (CPU Utilization).**

### **지원되는 알고리즘**
1. **FCFS (First Come First Serve).**
2. **SJF (Shortest Job First).**
3. **Round Robin.**
4. **우선순위 스케줄링 (Priority Scheduling)** (선점 및 비선점).
5. **다단계 피드백 큐 (Multi-Level Feedback Queue).**
6. **Rate Monotonic (실시간).**
7. **Earliest Deadline First (실시간).**

추가적으로, 프로그램은 다음과 같은 유용한 기능을 제공합니다:
- 수동 데이터 입력, 랜덤 데이터 생성, CSV 또는 JSON 파일을 통한 데이터 가져오기.
- 결과 및 보고서 내보내기.

---

## **2. 설치 방법**

### **시스템 요구 사항**
- **Python**: 버전 >= 3.8.
- **필수 라이브러리**: Matplotlib, Numpy, Tkinter 등.

### **설치 절차**
1. 저장소에서 소스를 복제하거나 다운로드:
   git clone 
   cd cpu-scheduler-simulator
2. 필요한 라이브러리 설치:
   pip install -r requirements.txt

   

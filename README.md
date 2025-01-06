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
 
### **구현된 알고리즘**
1. **FCFS (First-Come, First-Served)**:
   - 프로세스가 도착한 순서대로 실행.
   - 간단한 비선점 방식으로, 실행 중인 프로세스는 종료 시까지 실행됩니다.

2. **SJF (Shortest Job First)**:
   - 가장 짧은 실행 시간을 가진 프로세스를 우선 실행.
   - 선점/비선점 모두 지원 가능.

3. **Round Robin (RR)**:
   - 각 프로세스가 동일한 타임 슬라이스를 할당받아 순환 실행.
   - 타임 슬라이스 종료 후 Ready 상태로 전환됩니다.

4. **Priority Scheduling**:
   - 우선순위가 높은 프로세스를 우선 실행.
   - 선점 또는 비선점 방식으로 동작.

5. **Multi-Level Feedback Queue**:
   - 여러 큐를 사용하여 프로세스의 우선순위를 동적으로 변경하며 스케줄링.

6. **Rate Monotonic (실시간 스케줄링)**:
   - 주기가 짧은 작업에 높은 우선순위를 부여하는 고정 우선순위 알고리즘.

7. **Earliest Deadline First (EDF)**:
   - 가장 빠른 마감 기한을 가진 작업을 우선 실행.


---

## **2. 설치 방법**

### **시스템 요구 사항**
- **Python**: 버전 >= 3.8.
- **필수 라이브러리**: Matplotlib, Numpy, Tkinter 등.

### **설치 절차**
1. 저장소에서 소스를 복제하거나 다운로드: 
    ```bash
   git clone https://github.com/Duong2403/Professor-Junha-Jang-s-final-exam.git
   cd cpu-scheduler-simulator
2. 필요한 라이브러리 설치:
   pip install -r requirements.txt

## **3. 프로그램 실행 방법**

### **1단계: 데이터 입력 방법 선택**
- **수동 입력**: 프로세스의 ID, Arrival Time, Burst Time, Priority 정보를 직접 입력
- **랜덤 생성**: 프로세스 개수와 최대값을 설정하여 자동 생성
- **파일 입력**: CSV 또는 JSON 형식의 파일을 불러오기

### **2단계: 스케줄링 알고리즘 선택**
- 사용할 알고리즘 선택:
  - FCFS, SJF, Round Robin, Priority Scheduling 등
- 알고리즘별 매개변수 설정:
  - **Quantum** (Round Robin의 경우)
  - **큐 개수** (다단계 피드백 큐의 경우)

### **3단계: 스케줄링 시뮬레이션**
- **Start** 버튼을 눌러 시뮬레이션 시작
- 다음 정보 확인:
  - **간트 차트 (Gantt Chart)**: 프로세스 실행 순서 시각화
  - **I/O 작업 로그 (I/O Operations Log)**: I/O 활동 기록
  - **성능 지표 (Performance Metrics)**: 알고리즘 성능 정보
    ### **I/O 작업 및 인터럽트 처리**
1. **I/O 작업**:
   - 특정 시간에 프로세스가 **Waiting** 상태로 전환되며 I/O 작업이 시작됩니다.
   - I/O 작업이 완료되면 **Ready** 상태로 복귀합니다.

2. **타이머 인터럽트**:
   - Round Robin에서 타임 슬라이스가 종료되면 실행 중인 프로세스는 **Ready** 상태로 전환됩니다.

3. **우선순위 인터럽트**:
   - 높은 우선순위의 프로세스가 도착하면 현재 실행 중인 프로세스를 **Ready** 상태로 전환합니다.

### **4단계: 분석 및 결과 출력**
- 평균 대기 시간, 처리량, 문맥 전환 횟수 등 지표 확인
- 필요 시 보고서로 저장

## **5. 프로젝트 구조**

```
cpu-scheduler-simulator/
├── main.py # 메인 실행 파일
├── requirements.txt # 필수 라이브러리 목록
├── src/
│   ├── process/ # 프로세스 및 상태 정의
│   ├── schedulers/ # 스케줄링 알고리즘
│   ├── utils/ # 유틸리티 및 성능 계산
│   ├── visualization/ # 간트 차트 시각화
└── README.md # 사용 설명서
```

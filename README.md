###설치 및 실행 방법
환경 설정:
Python 3.8 이상 버전을 설치하세요.
다음 명령어를 사용하여 requirements.txt 파일에 명시된 필수 라이브러리를 설치하세요:
bash
Sao chép mã
pip install -r requirements.txt
프로그램 실행:
main.py 파일을 실행하여 시뮬레이션 인터페이스를 엽니다:
bash
Sao chép mã
python main.py
구현된 알고리즘 설명
FCFS (First-Come-First-Served):

프로세스는 도착 순서대로 처리되며, 선점이 없습니다.
SJF (Shortest Job First):

실행 시간이 가장 짧은 프로세스가 선택됩니다.
Round Robin (RR):

각 프로세스는 정해진 시간 간격(타임 슬라이스) 동안 CPU를 할당받습니다.
우선순위 스케줄링 (Priority Scheduling):

우선순위에 따라 프로세스가 선택됩니다 (선점 또는 비선점 방식 가능).
MLFQ (Multi-Level Feedback Queue):

여러 우선순위 큐를 사용하며, 우선순위를 점진적으로 낮추는 메커니즘이 적용됩니다.
Rate Monotonic (RM):

주기가 가장 짧은 프로세스가 선택됩니다 (실시간 시스템용).
Earliest Deadline First (EDF):

마감 시간이 가장 가까운 프로세스가 우선적으로 실행됩니다.
기능 사용 방법
프로세스 정보 입력:
수동 입력, 랜덤 생성, 또는 파일(CSV 또는 JSON)에서 가져오기.
알고리즘 선택:
FCFS, SJF, RR 등 목록에서 알고리즘을 선택하세요.
타임 슬라이스(Quantum)와 우선순위 조정(Priority Aging) 같은 매개변수를 설정할 수 있습니다.
결과 표시:
간트 차트 (Gantt Chart): 실행 스케줄을 시각적으로 나타냅니다.
성능 통계: 대기 시간, 반환 시간, CPU 사용률 등.
성능 비교: 알고리즘 간 성능 차이를 보여주는 차트 및 표.
입출력 예시
예제 입력:
csv
Sao chép mã
pid,arrival_time,burst_time,priority
1,0,5,1
2,1,3,2
예제 출력:
간트 차트: 프로세스가 실행되는 순서가 나타납니다.
통계:
평균 대기 시간: 2.5.
평균 반환 시간: 5.0.
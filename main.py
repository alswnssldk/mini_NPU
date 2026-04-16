import json
import time

def mac_operation(filter_arr, pattern_arr):
    total_score = 0
    n = len(filter_arr)

    for A in range(n):
        for B in range(n):
            total_score += filter_arr[A][B]*pattern_arr[A][B]
    return total_score

def compare_scores(score_a, score_b):
    if abs(score_a - score_b) < 1e-9:
        return "UNDECIDED"
    elif score_a > score_b:
        return "a"
    elif score_a < score_b:
        return "b"
    
def normalize_label(label):
    Cross = ["+", "cross", "Cross"]
    X = ["x", "X"]
    if label in Cross:
        return "Cross"
    elif label in X:
        return "X"
    else:
        return label


def get_3x3_input(prompt_message):
    while True: # 올바른 입력을 받을 때까지 무한 반복
        print(prompt_message)
        matrix = []
        
        try:
            # 3줄을 입력받아야 하므로 3번 반복합니다.
            for i in range(3):
            
                while True:
                    row_str = input(f"[{i+1}/3] 행 입력 (공백 구분): ")
                    string_list = row_str.split()
                    if not len(string_list) == 3:
                        print("3개가 아닙니다 다시 입력해주세요")
                    else:
                        break

                row_numbers = [float(x) for x in string_list]
                
                matrix.append(row_numbers)
                
            # 행이 정상적으로 3개가 다 채워졌는지 마지막으로 확인
            if len(matrix) == 3:
                return matrix
                
        except ValueError:
            print("❌ 입력 형식 오류: 숫자만 입력해주세요. 처음부터 다시 입력합니다.\n")
            
        except Exception as e:
            print(f"❌ 입력 형식 오류: {e} 처음부터 다시 입력합니다.\n")


def run_mode_1():
    print("=== Mini NPU Simulator (사용자 입력 모드) ===")
    
    filter_a = get_3x3_input("\n[필터 A 입력 (3x3)]")
    filter_b = get_3x3_input("\n[필터 B 입력 (3x3)]")
    pattern = get_3x3_input("\n[테스트 패턴 입력 (3x3)]")
    score_a = mac_operation(filter_a, pattern)
    score_b = mac_operation(filter_b, pattern)

    result = compare_scores(score_a, score_b)
    
    print("\n#---------------------------------------")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"판정: {result}")
    print("#---------------------------------------")





def run_mode_2(json_filepath="data.json"):
    print("Mini NPU simulator (json모드)")

    try:
        with open(json_filepath, 'r') as f:
            data = json.load(f)
        filters = data.get("filters", {})   # <--- ★ 필터들이 여기 전부 들어옵니다!
        patterns = data.get("patterns", {})

    except FileNotFoundError:
        print("파일없음")
        return

    Pass = 0
    Fail = 0
    Fail_log = []

    for key, value in patterns.items():
        try:
            part_list = key.split("_")
            N = int(part_list[1])

            filter_len_name = f"size_{N}"
            cross_filter = filters[filter_len_name]["Cross"]
            x_filter = filters[filter_len_name]["X"]
            if len(value["input"]) != N:    
                raise ValueError("길이 안맞음")

            
            result_label = normalize_label(value["expected"])
            Coross_score = mac_operation(cross_filter, value["input"])
            X_score = mac_operation(x_filter, value["input"])

            result = compare_scores(Coross_score, X_score)
            if result == "a":
                print("\n#---------------------------------------")
                print(f"A 점수: {Coross_score}")
                print(f"B 점수: {X_score}")
                print(f"판정: {result}")
                print(f"정답: {result_label}")
                if result_label == "Cross":
                    Pass += 1
                    print("#---------------------------------------")
                elif result_label == "X":
                    raise ValueError(f"정답 불일치 (기대값: Cross, 실제값: X)")
            elif result == "UNDECIDED":
                raise ValueError(f"점수 동률")

            if result == "b":
                print("\n#---------------------------------------")
                print(f"A 점수: {Coross_score}")
                print(f"B 점수: {X_score}")
                print(f"판정: {result}")
                print(f"정답: {result_label}")
                if result_label == "X":
                    Pass += 1
                    print("#---------------------------------------")
                elif result_label == "Cross":
                    raise ValueError(f"정답 불일치 (기대값: X, 실제값: Cross)")
            
        except Exception as e:
            Fail += 1
            Fail_log.append(f"[{key}] 사유 : {e}") 
            print("#---------------------------------------")
    
    print("\n#---------------------------------------")
    print("# [4] 결과 요약")
    print("#---------------------------------------")
    print(f"총 테스트: {Pass + Fail}개")
    print(f"통과: {Pass}개")
    print(f"실패: {Fail}개")
    
    if Fail_log:
        print("\n실패 케이스:")
        for log in Fail_log:
            print(f"- {log}")

def analyze_performance():
    sizes = [3, 5, 13, 25]
    print("\n[성능 분석 결과 (평균/10회)]")
    print(f"{'크기':<10} | {'평균 시간(ms)':<15} | {'연산 횟수(N²)'}")
    print("-" * 45)

    for n in sizes:
        # 1. n x n 크기의 가짜 데이터 생성 (모두 1로 채운 배열 등)
        test_filter = [[1.0] * n for _ in range(n)]
        test_pattern = [[1.0] * n for _ in range(n)]
        
        # 2. 10회 반복 측정
        start_time = time.perf_counter() # 측정 시작
        for _ in range(10):
            mac_operation(test_filter, test_pattern)
        end_time = time.perf_counter()   # 측정 종료
        
        # 3. 평균 시간 계산 (초 단위를 밀리초 ms로 변환: * 1000)
        avg_time_ms = ((end_time - start_time) / 10) * 1000
        
        # 4. 출력
        print(f"{n}x{n:<8} | {avg_time_ms:<15.6f} | {n*n}")



if __name__ == "__main__":
    while True:
        print("\n=== Mini NPU Simulator ===")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석 및 전체 성능 측정")
        print("0. 종료")

        choice = input("모드를 선택하세요: ")

        if choice == '1':
            run_mode_1()
        elif choice == '2':
            run_mode_2()
            analyze_performance()
        elif choice == '0':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 선택해주세요.")
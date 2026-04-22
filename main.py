import json
import time

def mac_operation(filter_arr, pattern_arr):
    total_score = 0
    n = len(filter_arr)

    for A in range(n):
        for B in range(n):
            total_score += filter_arr[A][B]*pattern_arr[A][B]
    return total_score

def compare_scores(scores_dict):
    max_score = max(scores_dict.values())

    top_filters = []

    for name, score in scores_dict.items():
        if abs(max_score - score) < 1e-9:
            top_filters.append(name)
    if len(top_filters) == 1:
        return top_filters[0]
    else:
        return "UNDECIDED"
    
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
    while True: 
        print(prompt_message)
        matrix = []
        
        try:
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

            if len(matrix) == 3:
                return matrix
                
        except ValueError:
            print("입력 형식 오류: 숫자만 입력해주세요. 처음부터 다시 입력합니다.\n")


def run_mode_1():
    print("=== Mini NPU Simulator (사용자 입력 모드) ===")
    
    filter_a = get_3x3_input("\n[필터 A 입력 (3x3)]")
    filter_b = get_3x3_input("\n[필터 B 입력 (3x3)]")
    pattern = get_3x3_input("\n[테스트 패턴 입력 (3x3)]")
    score_a = mac_operation(filter_a, pattern)
    score_b = mac_operation(filter_b, pattern)

    result = compare_scores({"A": score_a, "B": score_b})

    start_time = time.time()
    for _ in range(1000):
        mac_operation(filter_a, pattern)
    end_time = time.time()

    avg_time_ms = ((end_time - start_time) /1000) *1000
    print("\n#---------------------------------------")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간 | 평균/1000회 : {avg_time_ms:.10f}")
    print(f"판정: {result}")
    print("#---------------------------------------")

def run_mode_2(json_filepath="data.json"):
    print("Mini NPU simulator (json모드)")

    try:
        with open(json_filepath, 'r') as f:
            data = json.load(f)
        filters = data.get("filters", {})   
        patterns = data.get("patterns", {})

        for size_key in filters.keys():
            print(f"{size_key} 필터 로드 완료")

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

            target_filters = filters[filter_len_name]

            if len(value["input"]) != N:    
                raise ValueError("길이 안맞음")

            result_label = normalize_label(value["expected"])

            scores_dict = {}
            for filter_name, filter_matrix in target_filters.items():
                scores_dict[filter_name] = mac_operation(filter_matrix, value['input'])

            result = compare_scores(scores_dict)

            #========================================================================================>>>
            #========================================================================================>>>
            print("\n#---------------------------------------")
            for f_name, score in scores_dict.items():
                print(f"{f_name} 점수: {score}")
                
            print(f"판정: {result}")
            print(f"정답: {result_label}")
            if result == "UNDECIDED":
                raise ValueError("점수 동률")
            elif result.lower() == result_label.lower():
                Pass += 1
                print("#---------------------------------------")
            else:
                raise ValueError(f"정답 불일치 (기대값: {result_label}, 실제값: {result})")
            
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
        test_filter = [[1.0] * n for _ in range(n)]
        test_pattern = [[1.0] * n for _ in range(n)]
        
        start_time = time.perf_counter() 
        for _ in range(10):
            mac_operation(test_filter, test_pattern)
        end_time = time.perf_counter()  
        avg_time_ms = ((end_time - start_time) / 10) * 1000
        
        print(f"{n}x{n:<8} | {avg_time_ms:<15.6f} | {n*n}")



if __name__ == "__main__":
    try:
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
    except KeyboardInterrupt:
        print("프로그램을 종료합니다")
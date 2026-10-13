# git-study

Git 기본 사용법을 정리한 학습용 저장소입니다.

---

## 1. Git이란?

Git은 파일의 **변경 이력을 기록하고 관리하는 분산 버전 관리 시스템**입니다.

- 언제, 누가, 무엇을 바꿨는지 기록할 수 있습니다.
- 이전 버전으로 되돌릴 수 있습니다.
- 여러 작업 흐름(브랜치)을 나눠서 동시에 작업할 수 있습니다.

### 핵심 용어

| 용어 | 설명 |
| --- | --- |
| **Repository (저장소)** | 프로젝트와 그 변경 이력이 담긴 공간 (`.git` 폴더) |
| **Working Directory (작업 디렉터리)** | 실제로 파일을 수정하는 공간 |
| **Staging Area (스테이징 영역)** | 다음 커밋에 포함될 변경 사항을 모아두는 공간 |
| **Commit (커밋)** | 스테이징된 변경을 하나의 기록으로 저장한 것 |
| **Branch (브랜치)** | 독립적으로 작업할 수 있는 커밋의 흐름 |
| **HEAD** | 현재 작업 중인 브랜치 또는 커밋을 가리키는 포인터 |
| **Remote (원격 저장소)** | GitHub 등 인터넷에 있는 저장소 (기본 이름: `origin`) |

### 기본 흐름

```
Working Directory  ──git add──▶  Staging Area  ──git commit──▶  Repository
```

---

## 2. 설치 및 초기 설정

### 설치 확인

```bash
git --version
```

### 사용자 정보 설정 (최초 1회)

커밋에 기록될 이름과 이메일을 설정합니다.

```bash
git config --global user.name "본인 이름"
git config --global user.email "본인 이메일"
```

### 설정 확인

```bash
git config --list
```

### 기본 브랜치 이름을 main으로 설정 (선택)

```bash
git config --global init.defaultBranch main
```

---

## 3. 저장소 만들기 / 가져오기

### 새 저장소 만들기

이미 있는 폴더를 Git 저장소로 만듭니다.

```bash
git init
```

### 원격 저장소 복제하기

GitHub 등에 있는 저장소를 내 컴퓨터로 가져옵니다.

```bash
git clone https://github.com/사용자명/저장소명.git
```

---

## 4. 기본 작업 흐름

### 1단계: 상태 확인

```bash
git status
```

변경된 파일, 스테이징된 파일, 추적되지 않는 파일을 확인합니다. 작업 중 가장 자주 쓰는 명령어입니다.

### 2단계: 변경 내용 확인

```bash
git diff            # 아직 스테이징하지 않은 변경 내용
git diff --staged   # 스테이징된 변경 내용
```

### 3단계: 스테이징 (add)

```bash
git add 파일명       # 특정 파일만 추가
git add .           # 현재 폴더의 모든 변경 추가
git add -p          # 변경 조각(hunk) 단위로 골라서 추가
```

### 4단계: 커밋 (commit)

```bash
git commit -m "커밋 메시지"
```

커밋 메시지는 **무엇을, 왜** 바꿨는지 짧고 명확하게 적는 것이 좋습니다.

```bash
git commit -m "feat: 로그인 페이지 추가"
git commit -m "fix: 회원가입 시 이메일 검증 오류 수정"
```

### 5단계: 이력 확인

```bash
git log                     # 전체 커밋 이력
git log --oneline           # 한 줄씩 간략하게
git log --oneline --graph   # 브랜치 구조까지 그래프로 표시
```

---

## 5. 브랜치 (Branch)

브랜치는 작업을 격리하는 기능입니다. `main`을 깨끗하게 유지하고, 새 기능은 별도 브랜치에서 개발합니다.

```bash
git branch                 # 브랜치 목록 확인
git branch 새브랜치이름     # 브랜치 생성
git switch 브랜치이름       # 브랜치 이동 (최신 방식)
git switch -c 새브랜치이름  # 생성과 이동을 한 번에
git branch -d 브랜치이름    # 병합된 브랜치 삭제
```

> 이전 방식인 `git checkout`도 같은 역할을 하지만, 요즘은 `git switch`를 권장합니다.

### 브랜치 병합 (merge)

```bash
git switch main            # 합칠 대상 브랜치로 이동
git merge 작업브랜치        # 작업 브랜치의 변경을 main에 합침
```

### 충돌 (Conflict) 해결

같은 파일의 같은 부분을 서로 다르게 수정하면 충돌이 발생합니다.

1. `git status`로 충돌 파일을 확인합니다.
2. 파일 안의 `<<<<<<<`, `=======`, `>>>>>>>` 표시를 보고 남길 내용을 직접 고릅니다.
3. 수정이 끝나면 다시 스테이징하고 커밋합니다.

```bash
git add 충돌파일명
git commit
```

---

## 6. 원격 저장소 (Remote)

### 원격 저장소 연결

```bash
git remote add origin https://github.com/사용자명/저장소명.git
git remote -v                # 연결된 원격 저장소 확인
```

### 올리기 (push)

```bash
git push -u origin main      # 처음 올릴 때 (-u: 이후 기본 대상 설정)
git push                     # 이후에는 이 명령만으로 충분
```

### 내려받기 (fetch / pull)

```bash
git fetch origin             # 원격의 변경 정보만 가져오기 (병합은 안 함)
git pull origin main         # 원격 변경을 가져와서 현재 브랜치에 병합
```

---

## 7. 변경 취소 및 되돌리기

상황에 따라 적절한 명령어가 다릅니다.

| 상황 | 명령어 |
| --- | --- |
| 수정만 하고 아직 `add` 안 함 → 수정 취소 | `git restore 파일명` |
| `add` 했지만 아직 커밋 안 함 → 스테이징 취소 | `git restore --staged 파일명` |
| 마지막 커밋 메시지 수정 | `git commit --amend -m "새 메시지"` |
| 커밋을 취소하고 변경 내용은 유지 | `git reset --soft HEAD~1` |
| 특정 커밋의 변경을 되돌리는 **새 커밋** 만들기 (공유된 이력에 안전) | `git revert 커밋해시` |

> ⚠️ `git reset --hard`는 작업 내용을 **영구적으로 삭제**할 수 있으니 신중하게 사용하세요.

---

## 8. 자주 쓰는 명령어 요약

```bash
git init                    # 저장소 생성
git clone 주소              # 저장소 복제
git status                  # 상태 확인
git add .                   # 전체 스테이징
git commit -m "메시지"      # 커밋
git log --oneline           # 이력 확인
git switch -c 브랜치명      # 브랜치 생성 후 이동
git merge 브랜치명          # 브랜치 병합
git push                    # 원격에 올리기
git pull                    # 원격에서 내려받기
```

---

## 9. 커밋 메시지 작성 팁

권장 형식 (Conventional Commits 스타일):

```
<타입>: <요약>
```

| 타입 | 의미 |
| --- | --- |
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 변경 |
| `style` | 코드 포맷 등 동작에 영향 없는 변경 |
| `refactor` | 기능 변경 없이 코드 구조 개선 |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드, 설정 등 기타 작업 |

---

## 10. .gitignore

Git이 추적하지 않았으면 하는 파일(비밀번호, 빌드 결과물, 의존성 폴더 등)은 `.gitignore` 파일에 적습니다.

```gitignore
# 예시
node_modules/
.env
*.log
dist/
```

> 이미 커밋된 파일은 `.gitignore`에 추가해도 계속 추적됩니다. 추적을 끊으려면 `git rm --cached 파일명`을 사용하세요.

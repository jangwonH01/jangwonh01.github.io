# 사이트 생성기 (tools/generate.py)

이 블로그(`여행하는 요리사 JUHWANDAD`)는 정적 HTML 사이트이며,
`tools/generate.py`가 **글 원본(`posts/*.html`의 `<article>` 블록)**에서
홈·목록·글 페이지와 SEO 요소를 **재생성**한다.

## 무엇을 자동으로 채워주나
- 각 글: `<title>`, meta description, canonical, Open Graph
- 구조화 데이터(JSON-LD): 글=Article+BreadcrumbList, 레시피글=+Recipe
- 홈: WebSite + ItemList / 목록: CollectionPage
- 관련 글(같은 카테고리 3개) 내부 링크, 이전/다음 네비, 빵부스러기
- `sitemap.xml`, `favicon.svg`, `404.html`
- **멱등**: 아무것도 안 바꾸고 다시 실행해도 결과 동일

## 새 글 추가하는 법
1. `posts/travel-12.html`(또는 `food-12.html`) 생성. 파일 안에 아래 형태의 `<article>` 블록만 있으면 된다(나머지 head/nav/footer는 생성기가 채움):
   ```html
   <article class="post" id="travel-12">
       <div class="post-content">
           <div class="post-meta">
               <span class="post-tag">나라</span>
               <time>2026년 7월 5일</time>
               <span class="post-read">읽는 시간 5분</span>
           </div>
           <h2 class="post-title">글 제목</h2>
           <div class="post-body">
               <figure class="post-figure"><img src="이미지URL" alt="캡션" loading="lazy"><figcaption>캡션</figcaption></figure>
               <p>본문...</p>
               <h3>소제목</h3>
               <p>...</p>
           </div>
       </div>
   </article>
   ```
   (레시피글은 `class="post recipe-post"` + `recipe-info` + `ingredient-box` + `<ol class="recipe-steps">` 포함)
2. `python3 tools/generate.py` 실행 → 홈/목록/사이트맵/관련글 자동 갱신
3. `git add -A && git commit && git push` → 배포

## 주의
- 루트의 `google*.html`(Search Console 인증 파일)은 **삭제 금지**
- 실제 사진이 있으면 `figure`의 `src`를 교체(스톡보다 원본 사진이 품질·통과율에 유리)
- 같은 사진을 여러 장 중복 삽입하지 말 것(저품질 신호)

# web（静态问卷页面模板）

本目录可直接作为静态站点根目录部署（如 GitHub Pages）。

## 本地预览（联调）

1) 先生成题库与 blocks：
```bash
python survey_new/build_bank.py
```

2) 启动本地接收端（可选，用于模拟线上收数）：
```bash
python survey_new/receiver/local_receiver.py --port 8787
```

3) 启动静态文件服务器（在 web 目录下）：
```bash
python -m http.server 8000
```

4) 打开：
- Part 1：`http://localhost:8000/part1.html?PROLIFIC_PID=TEST_PID`
- Part 2：`http://localhost:8000/part2.html?PROLIFIC_PID=TEST_PID`

默认提交到 `http://localhost:8787/submit`（见 `config.js`）。


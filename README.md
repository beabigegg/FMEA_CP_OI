# FMEA-CP Full-Stack Analysis Platform

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![Framework](https://img.shields.io/badge/Backend-FastAPI-green.svg)
![Framework](https://img.shields.io/badge/Frontend-Vue.js-blue.svg)

## 1. 專案概覽 (Project Overview)

本專案是一個用於失效模式與效應分析 (FMEA) 和控制計畫 (CP) 文件的智慧分析平台，包含一個 FastAPI 後端和一個 Vue.js 前端。

它旨在將傳統的、基於 Excel 的工作流程，轉化為一個互動式的、可協作的 Web 應用程式。使用者可以上傳 FMEA/CP 文件，在一個並排的工作區中檢視它們，獲得 AI 驅動的關聯建議，並將其選擇永久儲存到資料庫中。

## 2. 核心功能 (Features)

- **全端架構**: 採用前後端分離模式，後端提供 RESTful API，前端提供動態單頁應用 (SPA)。
- **使用者認證**: 完整的使用者註冊、登入與頁面保護流程 (基於 JWT)。
- **文件儀表板**: 統一的儀表板，用於上傳新文件和檢視所有已上傳的文件列表。
- **互動式工作區**: 並排檢視 FMEA 和 CP 條目，方便對照和分析。
- **AI 智慧建議**: 點選 FMEA 條目時，自動呼叫 AI 服務，在 CP 列表中高亮推薦最相關的選項。
- **關聯儲存**: 允許使用者手動選擇並儲存 FMEA 與 CP 條目之間的多對多關聯。
- **角色型存取控制 (RBAC)**: 後端支援角色系統，例如，只有管理員能建立新帳號，並在首次啟動時自動建立初始管理員。

## 3. 技術堆疊 (Technology Stack)

### 後端 (Backend)
- **框架**: FastAPI
- **資料庫**: MySQL / MariaDB (via SQLAlchemy & PyMySQL)
- **資料處理**: Pandas
- **認證**: JWT, Passlib (Bcrypt)

### 前端 (Frontend)
- **框架**: Vue.js 3 (Composition API)
- **建構工具**: Vite
- **狀態管理**: Pinia
- **路由**: Vue Router
- **UI 元件庫**: Element Plus
- **API 客戶端**: Axios

## 4. 安裝與設定 (Setup and Installation)

### 4.1. 後端設定 (Backend Setup)

1.  **資料庫**: 確保 MySQL/MariaDB 服務正在運行。建立一個資料庫 (e.g., `db_A060`) 並使用 `database_schema.sql` 檔案來建立所有資料表。
2.  **環境變數**: 在專案根目錄下，建立 `.env` 檔案 (可參考 `README.md` 中的範本)，並填寫資料庫、DIFY AI、JWT `SECRET_KEY` 以及初始管理員的帳號密碼。
3.  **安裝依賴**: 在專案根目錄下，執行 `pip install -r requirements.txt`。

### 4.2. 前端設定 (Frontend Setup)

1.  **進入目錄**: `cd frontend`
2.  **安裝依賴**: `npm install`

## 5. 執行應用程式 (Running the Application)

您需要**開啟兩個獨立的終端機**來同時執行後端和前端伺服器。

### 終端機 1: 執行後端
在專案**根目錄**下執行：
```bash
uvicorn app:app --reload
```
後端將運行在 `http://127.0.0.1:8000`。

### 終端機 2: 執行前端
在 `frontend` **目錄**下執行：
```bash
npm run dev
```
前端開發伺服器將運行在一個不同的埠號上 (e.g., `http://127.0.0.1:5173`)。

### 5.1. 首次使用

1.  啟動後端後，檢查終端機輸出，確認初始管理員帳號已成功建立。
2.  在瀏覽器中開啟前端的 URL (e.g., `http://127.0.0.1:5173`)。
3.  使用您在 `.env` 中設定的管理員憑證進行登入。

## 6. API 文件

當後端伺服器運行時，您可以透過 `http://127.0.0.1:8000/docs` 存取自動生成的 API 互動式文件 (Swagger UI)。

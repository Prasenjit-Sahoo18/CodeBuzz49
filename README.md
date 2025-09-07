# CodeBuzz 🚀  
An AI-powered competitive coding platform with real-time proctoring, premium company-wise problem sets, and AI-driven solution guidance.  

https://codebuzz-puep.onrender.com/

## 📌 Problem Statement  
Most existing online coding platforms face three major challenges:  
1. **Lack of fairness** – Cheating during contests reduces credibility.  
2. **Unstructured preparation** – Learners cannot easily find company-wise problems for focused interview practice.  
3. **Limited personalized guidance** – Learners often struggle without intelligent support while solving problems.  

There is a need for a **fair, AI-powered, and career-focused coding ecosystem**.  

---

## 💡 Our Solution – CodeBuzz  
CodeBuzz is built to solve these problems through:  
- 🔒 **Real-time Camera Proctoring** → Ensures integrity and fairness during contests.  
- 🏆 **Regular Coding Contests** → Keeps learners engaged with real-world challenges.  
- 🎯 **Company-wise Tagged Problems** → Helps users prepare specifically for interviews at top tech companies.  
- 🤖 **AI-Powered Solution Generator** → Provides smart, step-by-step guidance for premium problems.  
- 💎 **Premium Subscriptions** → Unlock access to exclusive problems and AI features.  

With CodeBuzz, we bridge the gap between **learning, assessment, and employability**.  

---

## ⚙️ Tech Stack  
- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Django  
- **Database:** SQLite (development), PostgreSQL (production)  
- **AI Integration:** Google Gemini API  
- **Authentication:** Django built-in authentication  
- **Real-time Proctoring:** Camera tracking using MediaPipe / OpenCV  

---

## 📸 Screenshots

<img width="1470" height="840" alt="Screenshot 2025-09-07 at 3 08 09 PM" src="https://github.com/user-attachments/assets/de23d006-48b9-49a4-bb35-1ec7f7357ff0" />
<img width="1470" height="840" alt="Screenshot 2025-09-07 at 3 07 58 PM" src="https://github.com/user-attachments/assets/85648e4a-e695-4425-9a0e-6a3d9850883a" />
<img width="1470" height="749" alt="Screenshot 2025-09-07 at 3 07 13 PM" src="https://github.com/user-attachments/assets/8191f981-08c3-4916-9a52-5a9fc11ee015" />
<img width="1470" height="841" alt="Screenshot 2025-09-07 at 3 06 49 PM" src="https://github.com/user-attachments/assets/cbea3e3f-0a06-4b2c-b460-af6c3bc140c1" />
<img width="1470" height="838" alt="Screenshot 2025-09-07 at 3 06 33 PM" src="https://github.com/user-attachments/assets/067b11dd-d3cb-42a8-b530-1268723e73ad" />
<img width="1470" height="836" alt="Screenshot 2025-09-07 at 3 06 21 PM" src="https://github.com/user-attachments/assets/0a83c1d7-e5b3-45b2-9d0d-a8cbd982baa7" />
<img width="1470" height="837" alt="Screenshot 2025-09-07 at 3 06 08 PM" src="https://github.com/user-attachments/assets/7aff9aaf-43b9-4445-9942-2fa89091870e" />


---

## 🚀 Features  
- ✅ Online coding environment with syntax highlighting  
- ✅ Fair contests with real-time anti-cheating proctoring  
- ✅ AI-generated solutions for premium users  
- ✅ Company-wise tagging system for interview preparation  
- ✅ Premium subscriptions & user management  
- ✅ Code execution using HackerEarth API  


---

## 🔮 Future Enhancements  
- 📊 Personalized performance analytics & leaderboards  
- 🧑‍🤝‍🧑 Team coding challenges  
- 🌍 Support for multiple languages (C++, Java, Python, etc.)  
- 🎙️ Voice + AI mentor for real-time code debugging assistance  

---

## 🏆 Hackathon Context  
This project was built for **[Hackathon Name]** under the **EdTech / AI / Skill Development theme**, aiming to create a **trusted and intelligent coding platform** that prepares learners for the real world.  


---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- pip
- A HackerEarth API key

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd CODEBUZZ-master
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your HackerEarth API key as an environment variable:
   ```bash
   export HE_CLIENT_SECRET=your_hackerearth_api_key
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

---

## ☁️ Deployment

This application is configured for deployment to Render using the provided `render.yaml` configuration file.

### Environment Variables

Set the following environment variables in your Render dashboard:

- `SECRET_KEY` - Django secret key (generate a secure one)
- `DEBUG` - Set to "False" for production
- `HE_CLIENT_SECRET` - Your HackerEarth API key
- `DATABASE_URL` - PostgreSQL database URL (if using PostgreSQL)

### Deployment Steps

1. Fork this repository to your GitHub account
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Set the environment variables mentioned above
5. Deploy!

The build process will automatically:
- Install dependencies from requirements.txt
- Collect static files
- Run database migrations

---

## 🎥 Camera Proctoring Troubleshooting

If you're experiencing issues with the camera proctoring system, please refer to our detailed troubleshooting guide:

- [Proctoring Troubleshooting Guide](PROCTORING_TROUBLESHOOTING.md) - Comprehensive guide for diagnosing and resolving proctoring issues

### Quick Test Script

You can verify that the computer vision libraries are properly installed by running:

```bash
python test_cv.py
```

Expected output:
```
Testing computer vision library imports...
==================================================
NumPy version: 1.26.4
NumPy import successful
OpenCV version: 4.11.0
OpenCV import successful
MediaPipe version: 0.10.21
MediaPipe import successful
==================================================
All tests completed!
Computer vision libraries are ready.
```

If any libraries fail to import, the proctoring system will automatically disable itself and allow access to contests without camera monitoring.

Common issues and solutions:
1. **Camera Access Denied** - Check browser permissions and ensure no other applications are using the camera
2. **Proctoring Not Starting** - Verify contest settings and check browser console for errors
3. **Face Detection Issues** - Ensure proper lighting and camera positioning

You can also test your camera independently by navigating to `/camera-test/` in your browser.

---

## 📜 License  
This project is licensed under the MIT License.

# 🌊 AquaTrace – Smart Aquaculture Monitoring System

![AquaTrace Banner](assets/architecture.png)

**AquaTrace** is a smart, IoT-enabled aquaculture water quality monitoring system that combines **real-time sensing**, **web-based dashboards**, **predictive analytics**, and **alert mechanisms** to ensure healthy and sustainable fish farming.

It supports both **hardware-based monitoring** and **software simulation**, making it ideal for real-world deployment as well as academic and prototype use.

---

## 🚀 Key Features

- 🔐 Secure authentication (Sign up / Sign in)
- 🏡 Multi-farm & pond management
- 📊 Real-time water quality dashboard
- 🔁 Simulator ↔ Hardware mode switching
- 📈 Predictive analytics (fish growth & water replacement)
- 🚨 SMS alerts for unsafe water conditions
- 🧪 Works even **without physical hardware**

---

## 🧠 Parameters Monitored

| Parameter | Purpose |
|--------|--------|
| 🌡 Temperature | Fish metabolism & growth |
| 💧 pH Level | Water acidity / alkalinity |
| 🌬 Dissolved Oxygen | Fish survival |
| 🧪 Ammonia | Toxicity detection |
| 🌫 Turbidity | Water clarity |

---

## 🛠 Hardware Setup (Real Prototype)

This is the **actual working prototype** used in the project.

![Hardware Setup](assets/hardware_setup.jpg)

### 🔩 Components Used
- Arduino UNO
- Water temperature sensor
- pH sensor
- Turbidity sensor
- Dissolved oxygen sensor (simulated / optional)
- LCD Display (16x2)
- Breadboard & jumper wires
- Water samples for testing

---

## 🖥 Web Dashboard

The dashboard provides **real-time visualization** of all water parameters with charts, status indicators, and alerts.

![Dashboard Preview](assets/dashboard.png)

### Dashboard Capabilities
- Live graphs using Chart.js
- Parameter health status (Normal / Warning / Danger)
- Farm-wise data segregation
- Historical data analysis

---

## 🔁 Simulator & Hardware Mode

AquaTrace is designed to work in **two modes**:

| Mode | Description |
|----|-----------|
| 🧪 Simulator Mode | Generates realistic sensor data for testing |
| 🔌 Hardware Mode | Reads live data from Arduino |

You can switch modes **without changing the UI or database**.

---

## 📈 Prediction & Analytics

AquaTrace includes a prediction module that:
- Estimates **monthly fish growth**
- Suggests **water replacement schedules**
- Uses rule-based logic (extendable to ML)

---

## 🚨 SMS Alert System

When water quality becomes unsafe (e.g. high ammonia):

- ⚠️ Automatic SMS alert is sent
- 🔁 Alert cooldown prevents spam
- 📱 Uses Twilio API

Example alert:
```
AquaTrace Alert: Water quality unsafe. Change water immediately.
```

---

## 🧩 System Architecture

![System Architecture](assets/flow.png)

```
Sensors / Simulator
        ↓
  Flask Backend
        ↓
Prediction + Alerts
        ↓
    Database
        ↓
  Web Dashboard
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-----|-----------|
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Backend | Python, Flask |
| Database | SQLite |
| IoT | Arduino |
| Alerts | Twilio SMS API |
| Simulation | Python |

---

## 🎓 Academic & Practical Value

- ✔ Mini / Final Year Project ready
- ✔ Hardware + Software integration
- ✔ Resume & portfolio worthy
- ✔ Real-world applicability

---

## 🧠 One-Line Description (Resume / Viva)

> AquaTrace is a smart aquaculture monitoring system that provides real-time water quality analytics, predictive insights, and automated alerts using an IoT-enabled web platform.

---

## 🔮 Future Enhancements

- Machine learning-based prediction
- Mobile app integration
- Cloud IoT deployment
- WhatsApp & Email alerts
- AI-based fish health detection

---

## 👨‍💻 Authors

- **Amar Ayoob**
- Anusree A S  
- Dhyan Krishna Suresh K  
- Irfan Ibnul Haque A  

---

## 📜 License

This project is developed for academic and research purposes.

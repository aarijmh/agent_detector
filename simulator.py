import time
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.metrics import confusion_matrix, accuracy_score

# ==============================
# Advanced Agent (Red Team)
# ==============================
class AdvancedHumanLikeAgent:
    def __init__(self, username, password, human_like=True):
        self.username = username
        self.password = password
        self.human_like = human_like
        self.session_log = []
        self.ip_address = self.get_random_ip()

    def get_random_ip(self):
        residential_ips = [
            "192.168.1.45", "172.16.0.23", "10.0.0.56",
            "203.0.113.12", "198.51.100.34"
        ]
        ip = random.choice(residential_ips)
        self.session_log.append(("ip_selected", ip, time.time()))
        return ip

    def simulate_keystrokes(self, text):
        for char in text:
            delay = random.uniform(0.08, 0.3) if self.human_like else random.uniform(0.01, 0.05)
            time.sleep(delay)
            self.session_log.append(("keystroke", time.time()))

    def simulate_mouse_movement(self, start, end, steps=20):
        for i in range(steps):
            jitter_x = random.uniform(-2, 2) if self.human_like else 0
            jitter_y = random.uniform(-2, 2) if self.human_like else 0
            time.sleep(random.uniform(0.01, 0.05))
            self.session_log.append(("mouse_move", (start[0]+i, start[1]+i), time.time()))

    def browse_store(self):
        pages = ["home", "category", "product", "cart"]
        noise_pages = ["blog", "faq", "about-us", "terms"]
        for page in pages:
            dwell = random.uniform(2, 6) if self.human_like else random.uniform(0.5, 1.5)
            time.sleep(dwell)
            self.session_log.append(("page_view", page, time.time()))
            if self.human_like and random.random() < 0.3:
                noise_page = random.choice(noise_pages)
                time.sleep(random.uniform(1, 3))
                self.session_log.append(("page_view", noise_page, time.time()))

    def solve_captcha(self):
        delay = random.uniform(2, 5) if self.human_like else random.uniform(0.5, 1.0)
        time.sleep(delay)
        self.session_log.append(("captcha_solved", delay, time.time()))

    def handle_mfa(self):
        delay = random.uniform(3, 6) if self.human_like else random.uniform(0.5, 1.0)
        time.sleep(delay)
        self.session_log.append(("mfa_completed", delay, time.time()))

    def checkout(self):
        self.simulate_keystrokes(self.username)
        self.simulate_keystrokes(self.password)
        self.solve_captcha()
        self.handle_mfa()
        time.sleep(random.uniform(1, 3))
        self.session_log.append(("checkout", time.time()))

    def run(self):
        self.browse_store()
        self.checkout()
        return self.session_log

# ==============================
# Advanced Detector (Blue Team)
# ==============================
class AdvancedBehaviorDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.2)

    def extract_features(self, session_log):
        keystroke_times, mouse_moves, page_views = [], [], []
        captcha_time, mfa_time, ip_score = None, None, None

        for entry in session_log:
            if entry[0] == "keystroke":
                keystroke_times.append(entry[-1])
            elif entry[0] == "mouse_move":
                mouse_moves.append(entry[1])
            elif entry[0] == "page_view":
                page_views.append(entry[1])
            elif entry[0] == "captcha_solved":
                captcha_time = entry[1]
            elif entry[0] == "mfa_completed":
                mfa_time = entry[1]
            elif entry[0] == "ip_selected":
                ip_score = self.simulate_ip_reputation(entry[1])

        avg_keystroke_interval = np.mean(np.diff(keystroke_times)) if len(keystroke_times) > 1 else 0
        mouse_variance = np.var([math.dist(mouse_moves[i], mouse_moves[i+1]) for i in range(len(mouse_moves)-1)]) if len(mouse_moves) > 1 else 0
        nav_entropy = len(set(page_views)) / (len(page_views) + 1)
        captcha_time = captcha_time if captcha_time else 0
        mfa_time = mfa_time if mfa_time else 0
        ip_score = ip_score if ip_score else 0

        return [avg_keystroke_interval, mouse_variance, nav_entropy, captcha_time, mfa_time, ip_score]

    def simulate_ip_reputation(self, ip):
        if ip.startswith(("192", "10", "172")):
            return random.uniform(0.8, 1.0)
        else:
            return random.uniform(0.3, 0.7)

    def train(self, normal_sessions):
        features = [self.extract_features(s) for s in normal_sessions]
        self.model.fit(features)

    def detect(self, session_log):
        features = [self.extract_features(session_log)]
        prediction = self.model.predict(features)
        return "Human" if prediction[0] == 1 else "Agent"

# ==============================
# Simulation + Visualization
# ==============================
def simulate():
    # Generate sessions
    human_sessions = [AdvancedHumanLikeAgent("user", "pass", human_like=True).run() for _ in range(10)]
    agent_sessions = [AdvancedHumanLikeAgent("bot", "pass", human_like=False).run() for _ in range(10)]

    detector = AdvancedBehaviorDetector()
    detector.train(human_sessions)

    all_sessions = human_sessions + agent_sessions
    true_labels = ["Human"] * len(human_sessions) + ["Agent"] * len(agent_sessions)
    predictions = [detector.detect(s) for s in all_sessions]

    # Evaluate
    acc = accuracy_score(true_labels, predictions)
    cm = confusion_matrix(true_labels, predictions, labels=["Human", "Agent"])
    print("Accuracy:", acc)
    print("Confusion Matrix:\n", cm)

    # Extract features for visualization
    human_features = [detector.extract_features(s) for s in human_sessions]
    agent_features = [detector.extract_features(s) for s in agent_sessions]
    feature_names = ["Keystroke Interval", "Mouse Variance", "Nav Entropy", "CAPTCHA Time", "MFA Time", "IP Score"]

    # Plot feature distributions
    plt.figure(figsize=(12, 8))
    for i, name in enumerate(feature_names):
        plt.subplot(2, 3, i+1)
        plt.hist([f[i] for f in human_features], alpha=0.6, label="Human")
        plt.hist([f[i] for f in agent_features], alpha=0.6, label="Agent")
        plt.title(name)
        plt.legend()
    plt.tight_layout()
    plt.show()

    # Confusion matrix heatmap
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Human", "Agent"], yticklabels=["Human", "Agent"])
    plt.title("Confusion Matrix")
    plt.show()

# Run simulation
simulate()
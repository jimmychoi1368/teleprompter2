# -*- coding: utf-8 -*-
"""
智能提词器 - 语音识别驱动滚动
支持华为平板横竖屏，离线运行，蓝牙麦克风
"""

import os
import json
import re
from threading import Thread

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.animation import Animation
from kivy.metrics import dp, sp

# Android平台检测
try:
    from android.permissions import request_permissions, Permission
    from jnius import autoclass, cast
    ANDROID = True
except ImportError:
    ANDROID = False

# ==================== 关键词提取 ====================
STOP_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
    'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as',
    'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'between', 'under', 'again', 'further', 'then', 'once', 'here',
    'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few',
    'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
    'and', 'but', 'if', 'or', 'because', 'until', 'while', 'this',
    'that', 'these', 'those', 'am', 'it', 'its', 'i', 'me', 'my',
    'you', 'your', 'he', 'him', 'his', 'she', 'her', 'we', 'us',
    'our', 'they', 'them', 'their', 'what', 'which', 'who', 'whom'
}

def extract_keywords(text):
    """从文本中提取关键词（忽略停用词）"""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    return keywords

def split_sentences(text):
    """智能分句"""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

# ==================== Vosk语音识别器（Android原生SDK） ====================
class VoskRecognizer:
    """使用pyjnius桥接Vosk Android SDK"""
    
    def __init__(self, model_path, callback):
        self.callback = callback
        self.is_running = False
        self.recognizer = None
        self.model = None
        self.audio_record = None
        
        if ANDROID:
            self._init_android(model_path)
    
    def _init_android(self, model_path):
        """初始化Android Vosk"""
        try:
            # Java类
            self.Model = autoclass('org.vosk.Model')
            self.Recognizer = autoclass('org.vosk.Recognizer')
            self.AudioRecord = autoclass('android.media.AudioRecord')
            self.AudioFormat = autoclass('android.media.AudioFormat')
            self.MediaRecorder = autoclass('android.media.MediaRecorder')
            
            # 获取应用内部存储路径
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            
            # 模型路径（assets目录会被解压到files目录）
            files_dir = str(activity.getFilesDir().getAbsolutePath())
            full_model_path = os.path.join(files_dir, 'app', 'assets', 'vosk_model')
            
            # 如果模型在assets中，尝试其他路径
            if not os.path.exists(full_model_path):
                # 尝试直接访问
                for base in [files_dir, '/data/data/org.voiceprompter.teleprompter/files']:
                    for sub in ['app/assets/vosk_model', 'assets/vosk_model', 'vosk_model']:
                        test_path = os.path.join(base, sub)
                        if os.path.exists(test_path):
                            full_model_path = test_path
                            break
            
            print(f"[Vosk] Loading model from: {full_model_path}")
            
            # 初始化模型
            self.model = self.Model(full_model_path)
            self.recognizer = self.Recognizer(self.model, 16000.0)
            
            print("[Vosk] Model loaded successfully")
            
        except Exception as e:
            print(f"[Vosk] Init error: {e}")
            self.model = None
    
    def start(self):
        """开始录音识别"""
        if not ANDROID or self.model is None:
            print("[Vosk] Not available")
            return
        
        if self.is_running:
            return
        
        self.is_running = True
        Thread(target=self._record_loop, daemon=True).start()
    
    def _record_loop(self):
        """录音循环"""
        try:
            # 音频参数
            SAMPLE_RATE = 16000
            CHANNEL = self.AudioFormat.CHANNEL_IN_MONO
            ENCODING = self.AudioFormat.ENCODING_PCM_16BIT
            SOURCE = self.MediaRecorder.AudioSource.MIC  # 支持蓝牙麦克风
            
            # 计算缓冲区大小
            buffer_size = self.AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL, ENCODING)
            buffer_size = max(buffer_size, 8000)
            
            # 创建AudioRecord
            self.audio_record = self.AudioRecord(
                SOURCE, SAMPLE_RATE, CHANNEL, ENCODING, buffer_size
            )
            
            self.audio_record.startRecording()
            print("[Vosk] Recording started")
            
            # 读取缓冲区
            buffer = bytearray(buffer_size)
            
            while self.is_running:
                # 读取音频数据
                read_size = self.audio_record.read(buffer, 0, len(buffer))
                
                if read_size > 0:
                    # 转换为bytes
                    audio_bytes = bytes(buffer[:read_size])
                    
                    # 送入识别器
                    if self.recognizer.acceptWaveForm(audio_bytes, read_size):
                        result = self.recognizer.getResult()
                        self._process_result(result)
                    else:
                        partial = self.recognizer.getPartialResult()
                        self._process_partial(partial)
            
        except Exception as e:
            print(f"[Vosk] Record error: {e}")
        finally:
            if self.audio_record:
                try:
                    self.audio_record.stop()
                    self.audio_record.release()
                except:
                    pass
    
    def _process_result(self, result_json):
        """处理最终识别结果"""
        try:
            result = json.loads(result_json)
            text = result.get('text', '').strip()
            if text:
                self.callback(text, is_final=True)
        except:
            pass
    
    def _process_partial(self, partial_json):
        """处理部分识别结果"""
        try:
            result = json.loads(partial_json)
            text = result.get('partial', '').strip()
            if text:
                self.callback(text, is_final=False)
        except:
            pass
    
    def stop(self):
        """停止识别"""
        self.is_running = False

# ==================== 句子显示组件 ====================
class SentenceLabel(Label):
    """单个句子标签，支持高亮"""
    
    is_current = BooleanProperty(False)
    sentence_index = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(is_current=self._update_style)
        self.bind(size=self._update_bg, pos=self._update_bg)
        self._update_style()
    
    def _update_style(self, *args):
        """更新样式"""
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_current:
                # 当前句高亮黄色背景
                Color(1, 0.9, 0.3, 0.9)  # 明亮的黄色
            else:
                Color(0.15, 0.15, 0.2, 1)  # 深色背景
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        
        # 文字颜色
        if self.is_current:
            self.color = (0.1, 0.1, 0.1, 1)  # 黑色文字
        else:
            self.color = (0.9, 0.9, 0.95, 1)  # 浅色文字
    
    def _update_bg(self, *args):
        self._update_style()

# ==================== 主界面 ====================
class TeleprompterWidget(BoxLayout):
    """提词器主组件"""
    
    current_text = StringProperty('')
    sentences = ListProperty([])
    keywords_map = ListProperty([])  # 每个句子的关键词列表
    current_index = NumericProperty(0)
    is_listening = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(15)
        
        # 颜色主题
        with self.canvas.before:
            Color(0.08, 0.08, 0.12, 1)  # 深色背景
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # 语音识别器
        self.recognizer = None
        self.sentence_labels = []
        self.last_recognized = ''
        
        self._build_ui()
        
        # Android权限请求
        if ANDROID:
            Clock.schedule_once(self._request_permissions, 1)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _request_permissions(self, dt):
        """请求Android权限"""
        request_permissions([
            Permission.RECORD_AUDIO,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.BLUETOOTH,
            Permission.BLUETOOTH_ADMIN,
            Permission.BLUETOOTH_CONNECT
        ])
    
    def _build_ui(self):
        """构建界面"""
        
        # ===== 顶部：文案输入区 =====
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=0.25, spacing=dp(10))
        
        self.text_input = TextInput(
            hint_text='Paste or type your script here...',
            multiline=True,
            font_size=sp(18),
            background_color=(0.12, 0.12, 0.18, 1),
            foreground_color=(0.95, 0.95, 0.95, 1),
            hint_text_color=(0.5, 0.5, 0.55, 1),
            cursor_color=(0.3, 0.7, 1, 1),
            padding=[dp(15), dp(15)],
            size_hint_x=0.75
        )
        input_layout.add_widget(self.text_input)
        
        # 按钮区
        btn_layout = BoxLayout(orientation='vertical', size_hint_x=0.25, spacing=dp(8))
        
        self.load_btn = Button(
            text='LOAD',
            font_size=sp(16),
            background_color=(0.2, 0.6, 0.9, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        self.load_btn.bind(on_press=self.load_script)
        
        self.start_btn = Button(
            text='START',
            font_size=sp(16),
            background_color=(0.2, 0.8, 0.4, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        self.start_btn.bind(on_press=self.toggle_listening)
        
        self.reset_btn = Button(
            text='RESET',
            font_size=sp(16),
            background_color=(0.8, 0.3, 0.3, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        self.reset_btn.bind(on_press=self.reset_position)
        
        btn_layout.add_widget(self.load_btn)
        btn_layout.add_widget(self.start_btn)
        btn_layout.add_widget(self.reset_btn)
        
        input_layout.add_widget(btn_layout)
        self.add_widget(input_layout)
        
        # ===== 状态栏 =====
        self.status_label = Label(
            text='Ready - Paste script and press LOAD',
            font_size=sp(14),
            size_hint_y=None,
            height=dp(30),
            color=(0.6, 0.8, 1, 1)
        )
        self.add_widget(self.status_label)
        
        # ===== 中部：句子滚动显示区 =====
        self.scroll_view = ScrollView(
            size_hint_y=0.7,
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            bar_color=(0.4, 0.6, 1, 0.8),
            bar_inactive_color=(0.3, 0.3, 0.4, 0.5),
            scroll_type=['bars', 'content']
        )
        
        self.sentences_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(12),
            padding=[dp(10), dp(20)]
        )
        self.sentences_layout.bind(minimum_height=self.sentences_layout.setter('height'))
        
        self.scroll_view.add_widget(self.sentences_layout)
        self.add_widget(self.scroll_view)
        
        # 触摸重置
        self.scroll_view.bind(on_touch_down=self.on_scroll_touch)
    
    def load_script(self, instance):
        """加载文案"""
        text = self.text_input.text.strip()
        if not text:
            self.status_label.text = 'Please enter some text first!'
            return
        
        # 分句
        self.sentences = split_sentences(text)
        
        # 提取每个句子的关键词
        self.keywords_map = []
        for s in self.sentences:
            kw = extract_keywords(s)
            self.keywords_map.append(kw)
        
        # 清空并重建句子显示
        self.sentences_layout.clear_widgets()
        self.sentence_labels = []
        
        for i, sentence in enumerate(self.sentences):
            label = SentenceLabel(
                text=sentence,
                font_size=sp(28),
                text_size=(Window.width - dp(80), None),
                size_hint_y=None,
                halign='left',
                valign='middle',
                padding=[dp(20), dp(15)],
                sentence_index=i
            )
            label.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1] + dp(30)))
            
            self.sentence_labels.append(label)
            self.sentences_layout.add_widget(label)
        
        # 初始化
        self.current_index = 0
        self._highlight_current()
        
        # 初始化识别器
        if ANDROID and self.recognizer is None:
            self.recognizer = VoskRecognizer('vosk_model', self._on_speech_result)
        
        self.status_label.text = f'Loaded {len(self.sentences)} sentences. Press START to begin.'
    
    def toggle_listening(self, instance):
        """切换监听状态"""
        if not self.sentences:
            self.status_label.text = 'Please load a script first!'
            return
        
        if self.is_listening:
            self.is_listening = False
            self.start_btn.text = 'START'
            self.start_btn.background_color = (0.2, 0.8, 0.4, 1)
            if self.recognizer:
                self.recognizer.stop()
            self.status_label.text = 'Paused'
        else:
            self.is_listening = True
            self.start_btn.text = 'PAUSE'
            self.start_btn.background_color = (0.9, 0.6, 0.2, 1)
            if self.recognizer:
                self.recognizer.start()
            self.status_label.text = 'Listening... Speak now'
    
    def reset_position(self, instance):
        """重置到开头"""
        self.current_index = 0
        self._highlight_current()
        self._scroll_to_current(animate=False)
        self.status_label.text = 'Reset to beginning'
    
    def on_scroll_touch(self, instance, touch):
        """触摸滚动区域时的处理"""
        if self.scroll_view.collide_point(*touch.pos):
            # 检测点击了哪个句子
            for i, label in enumerate(self.sentence_labels):
                if label.collide_point(*touch.pos):
                    self.current_index = i
                    self._highlight_current()
                    return True
        return False
    
    @mainthread
    def _on_speech_result(self, text, is_final):
        """语音识别回调"""
        if not self.is_listening or not text:
            return
        
        text_lower = text.lower()
        words = set(re.findall(r'\b[a-zA-Z]+\b', text_lower))
        
        # 显示识别内容
        display_text = f'Heard: "{text}"'
        
        # 检查当前句子及后续句子的关键词匹配
        best_match_index = -1
        best_match_score = 0
        
        # 只检查当前句子到后面几句（避免跳太远）
        search_range = min(len(self.sentences), self.current_index + 5)
        
        for i in range(self.current_index, search_range):
            if i >= len(self.keywords_map):
                break
            
            sentence_keywords = set(self.keywords_map[i])
            if not sentence_keywords:
                continue
            
            # 计算匹配分数
            matches = words & sentence_keywords
            if matches:
                score = len(matches) / len(sentence_keywords)
                if score > best_match_score:
                    best_match_score = score
                    best_match_index = i
        
        # 如果有较好的匹配，移动到对应句子
        if best_match_index >= 0 and best_match_score >= 0.2:
            if best_match_index > self.current_index:
                self.current_index = best_match_index
                self._highlight_current()
                self._scroll_to_current(animate=True)
                display_text += f' → Moved to sentence {best_match_index + 1}'
        
        self.status_label.text = display_text
    
    def _highlight_current(self):
        """高亮当前句子"""
        for i, label in enumerate(self.sentence_labels):
            label.is_current = (i == self.current_index)
    
    def _scroll_to_current(self, animate=True):
        """滚动到当前句子"""
        if self.current_index >= len(self.sentence_labels):
            return
        
        label = self.sentence_labels[self.current_index]
        
        # 计算滚动位置（让当前句子显示在上方1/3处）
        scroll_height = self.sentences_layout.height - self.scroll_view.height
        if scroll_height <= 0:
            return
        
        # label在布局中的位置（从底部算起）
        label_y = label.y
        target_scroll = 1 - (label_y + label.height - self.scroll_view.height * 0.7) / scroll_height
        target_scroll = max(0, min(1, target_scroll))
        
        if animate:
            # 非匀速动画（先快后慢）
            anim = Animation(scroll_y=target_scroll, duration=0.4, t='out_cubic')
            anim.start(self.scroll_view)
        else:
            self.scroll_view.scroll_y = target_scroll

# ==================== 主应用 ====================
class TeleprompterApp(App):
    
    def build(self):
        # 设置窗口（桌面测试用）
        if not ANDROID:
            Window.size = (1280, 800)
        
        return TeleprompterWidget()
    
    def on_start(self):
        """应用启动"""
        print("[App] Teleprompter started")
    
    def on_pause(self):
        """应用暂停（Android）"""
        return True
    
    def on_resume(self):
        """应用恢复（Android）"""
        pass

if __name__ == '__main__':
    TeleprompterApp().run()



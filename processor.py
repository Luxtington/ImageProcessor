import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageEnhance
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root  # Главное окно приложения
        self.root.title("Image Processor App")  # Заголовок окна
        self.root.geometry("1200x800")  # Размер окна (ширина x высота)

        # Переменные для хранения изображений
        self.original_image = None  # Исходное изображение
        self.processed_image = None  # Обработанное изображение
        self.image_path = None  # Путь к файлу изображения
        self.photo_exif = None

        self.setup_ui()  # Создаем интерфейс

    def setup_ui(self):
        # Настройка темы и стилей (только визуальные изменения)
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TButton', padding=(10, 6))
        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Card.TLabelframe', padding=10)
        style.configure('Card.TLabelframe.Label', font=('Segoe UI', 11, 'bold'))
        style.configure('Horizontal.TScale', troughcolor='#e6e6e6')

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        main_frame.columnconfigure(0, weight=0)  # Левая панель
        main_frame.columnconfigure(1, weight=1)  # Правая панель
        main_frame.rowconfigure(0, weight=1)

        # Левая панель — прокручиваемая
        left_scrolled = VerticalScrolledFrame(main_frame, width=300)
        left_scrolled.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W), padx=(0, 10))
        left_panel = left_scrolled.interior  # Это твой внутренний фрейм для кнопок

        # Правая панель
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        # Оформленный блок предпросмотра
        preview_frame = ttk.Labelframe(right_panel, text='Предпросмотр', style='Card.TLabelframe')
        preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)
        preview_frame.rowconfigure(1, weight=1)

        # Заголовки над изображениями
        ttk.Label(preview_frame, text='Исходное', style='Header.TLabel').grid(row=0, column=0, padx=5, pady=(5, 0), sticky=tk.W)
        ttk.Label(preview_frame, text='Обработанное', style='Header.TLabel').grid(row=0, column=1, padx=5, pady=(5, 0), sticky=tk.W)

        # Все твои элементы — в left_panel, как раньше
        ttk.Button(left_panel, text="Загрузить изображение",
                   command=self.load_image).grid(row=0, column=0, pady=5, sticky=tk.W)

        ttk.Button(left_panel, text="Сохранить изображение",
                   command=self.save_image).grid(row=1, column=0, pady=5, sticky=tk.W)

        self.info_text = tk.Text(left_panel, height=15, width=35)
        self.info_text.grid(row=2, column=0, pady=10, sticky=tk.W)

        ttk.Button(left_panel, text="Скопировать текст",
                   command=self.copy_text).grid(row=3, column=0, pady=5, sticky=tk.W)

        ttk.Separator(left_panel, orient='horizontal').grid(row=4, column=0, pady=10, sticky=tk.W + tk.E)

        ttk.Button(left_panel, text="В градации серого",
                   command=self.convert_to_grayscale).grid(row=5, column=0, pady=5, sticky=tk.W)

        ttk.Label(left_panel, text="Яркость:").grid(row=6, column=0, pady=5, sticky=tk.W)
        self.brightness_var = tk.DoubleVar(value=1.0)
        ttk.Scale(left_panel, from_=0.1, to=2.0, variable=self.brightness_var,
                  command=self.adjust_brightness).grid(row=7, column=0, pady=5, sticky=tk.W + tk.E)

        ttk.Label(left_panel, text="Насыщенность:").grid(row=8, column=0, pady=5, sticky=tk.W)
        self.saturation_var = tk.DoubleVar(value=1.0)
        ttk.Scale(left_panel, from_=0.1, to=2.0, variable=self.saturation_var,
                  command=self.adjust_saturation).grid(row=9, column=0, pady=5, sticky=tk.W + tk.E)

        ttk.Label(left_panel, text="Контрастность:").grid(row=10, column=0, pady=5, sticky=tk.W)
        self.contrast_var = tk.DoubleVar(value=1.0)
        ttk.Scale(left_panel, from_=0.1, to=2.0, variable=self.contrast_var,
                  command=self.adjust_contrast).grid(row=11, column=0, pady=5, sticky=tk.W + tk.E)

        ttk.Button(left_panel, text="Показать гистограмму",
                   command=self.show_histogram).grid(row=12, column=0, pady=5, sticky=tk.W)

        ttk.Button(left_panel, text="Поворот на 90°",
                   command=self.rotate_image).grid(row=13, column=0, pady=5, sticky=tk.W)

        ttk.Button(left_panel, text="Линейная коррекция",
                   command=self.linear_correction).grid(row=14, column=0, pady=5, sticky=tk.W)

        ttk.Button(left_panel, text="Нелинейная коррекция",
                   command=self.nonlinear_correction).grid(row=15, column=0, pady=5, sticky=tk.W)

        ttk.Button(left_panel, text="Сбросить изменения",
                   command=self.reset_changes).grid(row=18, column=0, pady=5, sticky=tk.W)

        # Ползунок гамма-коррекции (используется линейной и нелинейной коррекцией)
        ttk.Separator(left_panel, orient='horizontal').grid(row=17, column=0, pady=8, sticky=tk.W + tk.E)
        ttk.Label(left_panel, text="Гамма:").grid(row=16, column=0, pady=5, sticky=tk.W)
        self.gamma_var = tk.DoubleVar(value=1.0)
        ttk.Scale(left_panel, from_=0.2, to=3.0, variable=self.gamma_var,
                  orient=tk.HORIZONTAL).grid(row=17, column=0, pady=5, sticky=tk.W + tk.E)

        # Метки для изображений: слева исходное, справа обработанное
        self.original_image_label = ttk.Label(preview_frame)
        self.original_image_label.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        self.image_label = ttk.Label(preview_frame)
        self.image_label.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Статус-бар
        self.status_label = ttk.Label(self.root, text='Готово', anchor='w', relief='sunken', padding=(10, 2))
        self.status_label.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def load_image(self):
        # Загрузка изображения через диалоговое окно
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif")]
        )

        if file_path:
            try:
                self.image_path = file_path # Сохраняем путь к файлу
                self.original_image = ImageOps.exif_transpose(Image.open(file_path))
                self.processed_image = self.original_image.copy()  # Создаем копию для обработки
                self.display_image()  # Отображаем изображение
                self.update_image_info()  # Обновляем информацию
                # Сбрасываем слайдеры в исходное положение
                self.brightness_var.set(1.0)
                self.saturation_var.set(1.0)
                self.contrast_var.set(1.0)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")

    def display_image(self):
        # Отображение изображения в интерфейсе
        if self.original_image:
            # Отображаем неизменяемое исходное изображение слева
            left_max_size = (380, 600)
            left_image = self.original_image.copy()
            left_image.thumbnail(left_max_size, Image.Resampling.LANCZOS)
            left_photo = ImageTk.PhotoImage(left_image)
            self.original_image_label.configure(image=left_photo)
            self.original_image_label.image = left_photo

        if self.processed_image:
            # Отображаем текущее обработанное изображение справа
            right_max_size = (380, 600)
            right_image = self.processed_image.copy()
            right_image.thumbnail(right_max_size, Image.Resampling.LANCZOS)
            right_photo = ImageTk.PhotoImage(right_image)
            self.image_label.configure(image=right_photo)
            self.image_label.image = right_photo

    def update_image_info(self):
        # Обновление информации об изображении
        if not self.image_path:
            return

        try:
            info = ""
            file_size = os.path.getsize(self.image_path)
            info += f"Размер файла: {file_size} байт ({file_size / 1024:.2f} KB)\n"

            # Свойства изображения
            img = Image.open(self.image_path)
            info += f"Разрешение: {img.width} x {img.height}\n"
            info += f"Формат: {img.format}\n"
            info += f"Цветовая модель: {img.mode}\n"

            # Глубина цвета в зависимости от режима
            if img.mode == 'L':  # Оттенки серого
                info += "Глубина цвета: 8 бит (градации серого)\n"
            elif img.mode == 'RGB':  # RGB
                info += "Глубина цвета: 24 бит (True Color)\n"
            elif img.mode == 'RGBA':  # RGB с альфа-каналом
                info += "Глубина цвета: 32 бит (True Color + Alpha)\n"
            else:
                info += f"Глубина цвета: информация о режиме {img.mode}\n"

            if self.original_image.getexif():
                info += "\nEXIF информация:\n"

                target_tags = {
                    306: 'DateTime',  # Дата и время
                    272: 'Model',  # Модель камеры
                    274: 'Orientation',  # Ориентация
                    305: 'Software',  # Программное обеспечение
                    33437: 'FNumber',  # Диафрагма
                    33434: 'ExposureTime',  # Выдержка
                    34855: 'ISOSpeedRatings',  # ISO
                    37386: 'FocalLength',  # Фокусное расстояние
                    42036: 'LensModel',  # Модель объектива
                    41986: 'ExposureMode',  # Режим экспозиции
                    41987: 'WhiteBalance',  # Баланс белого
                    41988: 'DigitalZoomRatio',  # Цифровой зум
                    41989: 'FocalLengthIn35mmFilm',  # Эквивалентное фокусное расстояние
                    41990: 'SceneCaptureType',  # Тип сцены
                    41991: 'GainControl',  # Управление усилением
                    41992: 'Contrast',  # Контраст
                    41993: 'Saturation',  # Насыщенность
                    41994: 'Sharpness',  # Резкость
                    33432: 'Copyright',  # Авторские права
                    315: 'Artist',  # Автор
                    316: 'HostComputer',  # Компьютер
                    282: 'XResolution',  # Разрешение по X
                    283: 'YResolution',  # Разрешение по Y
                    296: 'ResolutionUnit',  # Единица разрешения
                    531: 'YCbCrPositioning',  # Позиционирование YCbCr
                    34665: 'ExifOffset',  # Смещение EXIF
                    33445: 'Flash',  # Вспышка
                    36867: 'DateTimeOriginal',  # Дата съемки
                    36868: 'DateTimeDigitized',  # Дата оцифровки
                    37377: 'ShutterSpeedValue',  # Значение выдержки
                    37378: 'ApertureValue',  # Значение диафрагмы
                    37379: 'BrightnessValue',  # Значение яркости
                    37380: 'ExposureBiasValue',  # Компенсация экспозиции
                    37381: 'MaxApertureValue',  # Максимальная диафрагма
                    37382: 'SubjectDistance',  # Расстояние до объекта
                    37383: 'MeteringMode',  # Режим замера
                    37384: 'LightSource',  # Источник света
                    37396: 'SubjectArea',  # Область объекта
                    41486: 'FocalPlaneXResolution',  # Разрешение фокальной плоскости X
                    41487: 'FocalPlaneYResolution',  # Разрешение фокальной плоскости Y
                    41488: 'FocalPlaneResolutionUnit',  # Единица разрешения фокальной плоскости
                    41492: 'SubjectLocation',  # Расположение объекта
                    41493: 'ExposureIndex',  # Индекс экспозиции
                    41495: 'SensingMethod',  # Метод сенсора
                    41728: 'FileSource',  # Источник файла
                    41729: 'SceneType',  # Тип сцены
                    41730: 'CFAPattern',  # Паттерн CFA
                    41985: 'FlashPixVersion',  # Версия FlashPix
                    41995: 'SubjectDistanceRange',  # Диапазон расстояния до объекта
                    42016: 'ImageUniqueID',  # Уникальный ID изображения
                    42017: 'CameraOwnerName',  # Имя владельца камеры
                    42018: 'BodySerialNumber',  # Серийный номер корпуса
                    42019: 'LensSpecification',  # Спецификация объектива
                    42020: 'LensMake',  # Производитель объектива
                    42022: 'LensSerialNumber',  # Серийный номер объектива
                }

                all_exif = self.original_image.getexif()

                displayed_count = 0
                for tag_id, value in all_exif.items():
                    if tag_id in target_tags and displayed_count < 10:
                        tag_name = target_tags[tag_id]
                        info += f"{tag_name}: {value}\n"
                        displayed_count += 1

            else:
                info += "\nEXIF информация отсутствует (загрузите фото напрямую с камеры, так как приложения автоматически удаляют EXIF при загрузке)\n"

            info += f"\nДополнительная информация:\n"
            info += f"Соотношение сторон: {img.width / img.height:.2f}\n"
            info += f"Общее количество пикселей: {img.width * img.height}\n"

            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить информацию: {str(e)}")

    def copy_text(self):
        try:
            # Получаем весь текст из текстового поля
            text_to_copy = self.info_text.get(1.0, tk.END).strip()

            # Очищаем буфер обмена и добавляем туда текст
            self.root.clipboard_clear()
            self.root.clipboard_append(text_to_copy)

            # Сообщаем пользователю об успешном копировании
            messagebox.showinfo("Успех", "Текст скопирован в буфер обмена")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скопировать текст: {str(e)}")


    def convert_to_grayscale(self):
        # Преобразование изображения в оттенки серого
        if self.processed_image:
            try:
                if self.processed_image.mode != 'L':  # Если еще не в grayscale
                    self.processed_image = self.processed_image.convert('L')  # Конвертируем
                self.display_image()  # Обновляем отображение
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось преобразовать в серый: {str(e)}")

    def adjust_brightness(self, value):
        # Коррекция яркости изображения
        if self.processed_image:
            try:
                # Создаем усилитель яркости на основе оригинального изображения
                enhancer = ImageEnhance.Brightness(self.original_image)
                # Применяем коррекцию (value от 0.1 до 2.0)
                self.processed_image = enhancer.enhance(float(value))
                self.display_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить яркость: {str(e)}")

    def adjust_contrast(self, value):
        # Коррекция контрастности
        if self.processed_image:
            try:
                enhancer = ImageEnhance.Contrast(self.processed_image)
                self.processed_image = enhancer.enhance(float(value))
                self.display_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить контрастность: {str(e)}")

    def adjust_saturation(self, value):
        # Коррекция насыщенности (только для цветных изображений)
        if self.processed_image and self.processed_image.mode != 'L':
            try:
                enhancer = ImageEnhance.Color(self.processed_image)
                self.processed_image = enhancer.enhance(float(value))
                self.display_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить насыщенность: {str(e)}")

    def show_histogram(self):
        # Показать гистограмму изображения (распределение яркостей пикселей)
        if not self.processed_image:
            return

        # Подготовка данных: исходное и обработанное изображения
        def to_cv(img: Image.Image):
            if img.mode == 'L':
                return np.array(img), ['Grayscale'], ['black']
            arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            return arr, ['Blue', 'Green', 'Red'], ['b', 'g', 'r']

        orig_cv, orig_channels, orig_colors = to_cv(self.original_image) if self.original_image else (None, [], [])
        proc_cv, proc_channels, proc_colors = to_cv(self.processed_image)

        # Создаем новое окно для гистограммы
        hist_window = tk.Toplevel(self.root)  # Toplevel - дочернее окно
        hist_window.title("Гистограмма: исходное (сверху) и обработанное (снизу)")
        hist_window.geometry("900x700")

        # Создаем 2 подграфика: сверху исходное, снизу обработанное
        fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

        # Верх: исходное
        if orig_cv is not None:
            if self.original_image.mode == 'L':
                hist = cv2.calcHist([orig_cv], [0], None, [256], [0, 256])
                ax_top.plot(hist, color=orig_colors[0], label=orig_channels[0])
            else:
                for i, col in enumerate(orig_colors):
                    hist = cv2.calcHist([orig_cv], [i], None, [256], [0, 256])
                    ax_top.plot(hist, color=col, label=orig_channels[i])
            ax_top.set_title('Исходное изображение')
            ax_top.set_ylabel('Пиксели')
            ax_top.legend()
            ax_top.grid(True)

        # Низ: обработанное
        if self.processed_image.mode == 'L':
            hist = cv2.calcHist([proc_cv], [0], None, [256], [0, 256])
            ax_bottom.plot(hist, color=proc_colors[0], label=proc_channels[0])
        else:
            for i, col in enumerate(proc_colors):
                hist = cv2.calcHist([proc_cv], [i], None, [256], [0, 256])
                ax_bottom.plot(hist, color=col, label=proc_channels[i])
        ax_bottom.set_title('Обработанное изображение')
        ax_bottom.set_xlabel('Уровень интенсивности')
        ax_bottom.set_ylabel('Пиксели')
        ax_bottom.legend()
        ax_bottom.grid(True)

        fig.tight_layout()

        # Встраиваем график в Tkinter окно
        canvas = FigureCanvasTkAgg(fig, master=hist_window)
        canvas.draw()  # Рисуем график
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Растягиваем на все окно

    def rotate_image(self):
        # Поворот изображения на 90 градусов
        if self.processed_image:
            try:
                # rotate(угол, expand=True - автоматически меняет размер canvas)
                self.processed_image = self.processed_image.rotate(90, expand=True)
                self.display_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось повернуть изображение: {str(e)}")

    def linear_correction(self):
        # Линейное растяжение гистограммы (улучшение контраста)
        if self.processed_image:
            try:
                # Приводим к оттенкам серого на время коррекции (работает и для RGB-фото)
                gray_img = self.processed_image.convert('L')
                # ВАЖНО: работаем в float, чтобы избежать переполнений uint8 при (x - min)
                img_array = np.array(gray_img).astype('float32')
                # Растяжение по перцентилям (устойчивее, даёт видимый эффект)
                p_low, p_high = np.percentile(img_array, (1, 99))
                if p_high == p_low:
                    # Плоская гистограмма — изменений не будет
                    messagebox.showinfo("Информация", "Линейная коррекция: нет диапазона яркостей (изображение однородное).")
                    return
                corrected = (img_array - p_low) * (255.0 / (p_high - p_low))
                # Доп. гамма-коррекция поверх линейного растяжения, если ползунок не 1.0
                gamma = float(self.gamma_var.get()) if hasattr(self, 'gamma_var') else 1.0
                if abs(gamma - 1.0) > 1e-3:
                    safe_gamma = max(1e-6, gamma)
                    base = np.clip(corrected, 0.0, 255.0) / 255.0
                    base = np.maximum(base, 1e-12)
                    corrected = 255.0 * (base ** (1.0 / safe_gamma))
                corrected = np.clip(corrected, 0, 255)
                corrected = np.nan_to_num(corrected, nan=0.0, posinf=255.0, neginf=0.0)
                self.processed_image = Image.fromarray(corrected.astype('uint8'))
                self.display_image()
                try:
                    self.status_label.configure(text=f"Линейная коррекция: p1={p_low:.1f}, p99={p_high:.1f}, gamma={gamma:.2f}")
                except Exception:
                    pass
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось применить линейную коррекцию: {str(e)}")

    def nonlinear_correction(self):
        # Нелинейная коррекция (гамма-коррекция)
        if self.processed_image and self.processed_image.mode == 'L':  # Только для grayscale
            try:
                img_array = np.array(self.processed_image).astype('float32')  # Конвертируем в float
                # Гамма-коррекция: 255 * (x/255)^(1/гамма)
                gamma = float(self.gamma_var.get()) if hasattr(self, 'gamma_var') else 1.5
                safe_gamma = max(1e-6, gamma)
                base = np.clip(img_array / 255.0, 0.0, 1.0)
                base = np.maximum(base, 1e-12)
                corrected = 255.0 * (base ** (1.0 / safe_gamma))
                corrected = np.clip(corrected, 0.0, 255.0)
                corrected = np.nan_to_num(corrected, nan=0.0, posinf=255.0, neginf=0.0)
                # Конвертируем обратно в 8-битное изображение
                self.processed_image = Image.fromarray(corrected.astype('uint8'))
                self.display_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось применить нелинейную коррекцию: {str(e)}")

    def reset_changes(self):
        # Сброс всех изменений к исходному изображению
        if self.original_image:
            self.processed_image = self.original_image.copy()  # Восстанавливаем копию оригинала
            # Сбрасываем слайдеры
            self.brightness_var.set(1.0)
            self.saturation_var.set(1.0)
            self.contrast_var.set(1.0)
            self.display_image()  # Обновляем отображение

    def save_image(self):
        # Сохранение обработанного изображения
        if self.processed_image:
            # Диалог выбора места сохранения
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",  # Расширение по умолчанию
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    self.processed_image.save(file_path)  # Сохраняем изображение
                    messagebox.showinfo("Успех", "Изображение успешно сохранено!")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {str(e)}")

class VerticalScrolledFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Создаем канвас + фрейм внутри + скроллбар
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=False)

        canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscrollbar.config(command=canvas.yview)

        # Сбрасываем положение при открытии
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Создаем внутренний фрейм
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        # Прокрутка колесом
        def _on_mousewheel(event):
            canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        interior.bind_all("<MouseWheel>", _on_mousewheel)

        # Обновляем размеры при изменении внутреннего фрейма
        def _configure_interior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        # Обновляем ширину canvas при изменении размера
        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

def main():
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
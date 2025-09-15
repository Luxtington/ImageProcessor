# Импортируем необходимые библиотеки
import tkinter as tk  # Основная библиотека для создания графического интерфейса (GUI)
from tkinter import ttk, filedialog, messagebox  # Дополнительные компоненты GUI:
# ttk - стилизованные виджеты, filedialog - диалоги выбора файлов, messagebox - всплывающие окна
from PIL import Image, ImageTk, ImageOps, ImageEnhance  # Библиотека для работы с изображениями:
# Image - загрузка/сохранение, ImageTk - интеграция с Tkinter, ImageEnhance - коррекция изображений
import cv2  # OpenCV - основная библиотека компьютерного зрения
import numpy as np  # NumPy - библиотека для математических операций с массивами
import os  # Для работы с файловой системой (получение размера файла и т.д.)
from PIL.ExifTags import TAGS  # Для чтения EXIF-метаданных фотографий
import matplotlib.pyplot as plt  # Для построения графиков и гистограмм
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Для встраивания графиков в Tkinter


class ImageProcessorApp:
    def __init__(self, root):
        # Конструктор класса - инициализация приложения
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
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
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

        # Все твои элементы — в left_panel, как раньше
        ttk.Button(left_panel, text="Загрузить изображение",
                   command=self.load_image).grid(row=0, column=0, pady=5, sticky=tk.W)

        ttk.Button(left_panel, text="Сохранить изображение",
                   command=self.save_image).grid(row=1, column=0, pady=5, sticky=tk.W)

        self.info_text = tk.Text(left_panel, height=15, width=35)
        self.info_text.grid(row=2, column=0, pady=10, sticky=tk.W)

        ttk.Separator(left_panel, orient='horizontal').grid(row=3, column=0, pady=10, sticky=tk.W + tk.E)

        ttk.Button(left_panel, text="В градации серого",
                   command=self.convert_to_grayscale).grid(row=4, column=0, pady=5, sticky=tk.W)

        ttk.Label(left_panel, text="Яркость:").grid(row=5, column=0, pady=5, sticky=tk.W)
        self.brightness_var = tk.DoubleVar(value=1.0)
        ttk.Scale(left_panel, from_=0.1, to=2.0, variable=self.brightness_var,
                  command=self.adjust_brightness).grid(row=6, column=0, pady=5, sticky=tk.W + tk.E)

        ttk.Label(left_panel, text="Насыщенность:").grid(row=7, column=0, pady=5, sticky=tk.W)
        self.saturation_var = tk.DoubleVar(value=1.0)
        ttk.Scale(left_panel, from_=0.1, to=2.0, variable=self.saturation_var,
                  command=self.adjust_saturation).grid(row=8, column=0, pady=5, sticky=tk.W + tk.E)

        ttk.Label(left_panel, text="Контрастность:").grid(row=9, column=0, pady=5, sticky=tk.W)
        self.contrast_var = tk.DoubleVar(value=1.0)
        ttk.Scale(left_panel, from_=0.1, to=2.0, variable=self.contrast_var,
                  command=self.adjust_contrast).grid(row=10, column=0, pady=5, sticky=tk.W + tk.E)

        ttk.Button(left_panel, text="Показать гистограмму",
                   command=self.show_histogram).grid(row=11, column=0, pady=5, sticky=tk.W)

        ttk.Button(left_panel, text="Поворот на 90°",
                   command=self.rotate_image).grid(row=12, column=0, pady=5, sticky=tk.W)

        ttk.Button(left_panel, text="Линейная коррекция",
                   command=self.linear_correction).grid(row=13, column=0, pady=5, sticky=tk.W)

        ttk.Button(left_panel, text="Нелинейная коррекция",
                   command=self.nonlinear_correction).grid(row=14, column=0, pady=5, sticky=tk.W)

        ttk.Button(left_panel, text="Сбросить изменения",
                   command=self.reset_changes).grid(row=15, column=0, pady=5, sticky=tk.W)

        # Метка для изображения
        self.image_label = ttk.Label(right_panel)
        self.image_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def load_image(self):
        # Загрузка изображения через диалоговое окно
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif")]
        )

        if file_path:
            try:
                self.image_path = file_path  # Сохраняем путь к файлу
                self.original_image = Image.open(file_path)  # Открываем изображение через PIL
                self.processed_image = self.original_image.copy()  # Создаем копию для обработки
                self.display_image()  # Отображаем изображение
                self.update_image_info()  # Обновляем информацию
                # Сбрасываем слайдеры в исходное положение
                self.brightness_var.set(1.0)
                self.saturation_var.set(1.0)
                self.contrast_var.set(1.0)
            except Exception as e:
                # Обработка ошибок загрузки
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")

    def display_image(self):
        # Отображение изображения в интерфейсе
        if self.processed_image:
            # Масштабируем изображение под размер окна
            max_size = (800, 600)
            image = self.processed_image.copy()  # Создаем копию
            image.thumbnail(max_size, Image.Resampling.LANCZOS)  # Изменяем размер с высоким качеством

            # Конвертируем изображение для Tkinter
            photo = ImageTk.PhotoImage(image) #данные изображения, которые Tkinter может отобразить.
            self.image_label.configure(image=photo)  # Устанавливаем изображение в метку.  Виджет теперь знает, что ему нужно отрисовать это изображение.
            self.image_label.image = photo  # Сохраняем ссылку (важно для предотвращения сборки мусора)

    def update_image_info(self):
        # Обновление информации об изображении
        if not self.image_path:
            return

        try:
            info = ""
            # Информация о размере файла
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

                # ЖЕСТКИЙ СПИСОК ТЕГОВ КОТОРЫЕ МЫ ХОТИМ ВЫВЕСТИ
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

                info += "\n" + "=" * 50 + "\n"
                info += "ОТОБРАЖАЕМЫЕ ТЕГИ:\n"

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

        # Конвертируем в формат OpenCV (numpy array)
        if self.processed_image.mode == 'L':  # Grayscale
            img_cv = np.array(self.processed_image)  # Просто конвертируем в массив
            channels = ['Grayscale']
            colors = ['black']
        else:  # Color image
            # Конвертируем PIL Image в numpy array и меняем цветовую модель RGB → BGR (для OpenCV)
            img_cv = cv2.cvtColor(np.array(self.processed_image), cv2.COLOR_RGB2BGR)
            channels = ['Blue', 'Green', 'Red']  # Каналы в порядке BGR
            colors = ['b', 'g', 'r']  # Цвета для графиков

        # Создаем новое окно для гистограммы
        hist_window = tk.Toplevel(self.root)  # Toplevel - дочернее окно
        hist_window.title("Гистограмма изображения")
        hist_window.geometry("800x600")

        # Создаем график matplotlib
        fig, ax = plt.subplots(figsize=(8, 6))

        if self.processed_image.mode == 'L':
            # Вычисляем гистограмму для grayscale
            # calcHist([изображения], [каналы], маска, [количество бинов], [диапазон])
            hist = cv2.calcHist([img_cv], [0], None, [256], [0, 256])
            ax.plot(hist, color=colors[0], label=channels[0])  # Рисуем график
        else:
            # Для цветного изображения рисуем гистограммы для каждого канала
            for i, col in enumerate(colors):
                hist = cv2.calcHist([img_cv], [i], None, [256], [0, 256])
                ax.plot(hist, color=col, label=channels[i])

        # Настраиваем внешний вид графика
        ax.set_title('Гистограмма изображения')
        ax.set_xlabel('Уровень интенсивности')  # По X - значения яркости (0-255)
        ax.set_ylabel('Количество пикселей')  # По Y - количество пикселей с данной яркостью
        ax.legend()  # Показываем легенду
        ax.grid(True)  # Включаем сетку

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
        if self.processed_image and self.processed_image.mode == 'L':  # Только для grayscale
            try:
                img_array = np.array(self.processed_image)  # Конвертируем в numpy array
                # Линейное растяжение: (x - min) * (255 / (max - min))
                min_val = np.min(img_array)  # Минимальное значение яркости
                max_val = np.max(img_array)  # Максимальное значение яркости
                corrected = (img_array - min_val) * (255.0 / (max_val - min_val))
                # Конвертируем обратно в PIL Image
                self.processed_image = Image.fromarray(corrected.astype('uint8'))
                self.display_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось применить линейную коррекцию: {str(e)}")

    def nonlinear_correction(self):
        # Нелинейная коррекция (гамма-коррекция)
        if self.processed_image and self.processed_image.mode == 'L':  # Только для grayscale
            try:
                img_array = np.array(self.processed_image).astype('float32')  # Конвертируем в float
                # Гамма-коррекция: 255 * (x/255)^(1/гамма)
                gamma = 1.5  # Коэффициент гамма-коррекции
                corrected = 255 * (img_array / 255) ** (1 / gamma)
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
    # Главная функция приложения
    root = tk.Tk()  # Создаем главное окно Tkinter
    app = ImageProcessorApp(root)  # Создаем экземпляр нашего приложения
    root.mainloop()  # Запускаем главный цикл обработки событий (как в Java Swing)


# Стандартная конструкция для Python:
# Если этот файл запущен напрямую (а не импортирован как модуль)
if __name__ == "__main__":
    main()  # Вызываем главную функцию
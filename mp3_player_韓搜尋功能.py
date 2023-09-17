#音樂播放器 v1.3.4 20230830

# 導入所需的模組
import os  # 操作系統相關功能
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # 隱藏Pygame啟動顯示訊息
import re  # 正則表達式模組
import pygame  # 音樂播放引擎
import random  # 生成隨機數
import threading
import pyautogui  # 調整解析度
from pygame import mixer  # 音樂播放器的額外功能
from tkinter import ttk, Tk, Label, Listbox, SINGLE, Button, PhotoImage, LEFT, Menu, END, mainloop, ACTIVE, RAISED  # GUI元件
import tkinter as tk  # Tkinter模組
from mutagen.mp3 import MP3  # 讀取MP3檔案的metadata信息


# 定義一個函數，用於從指定資料夾中找尋特定副檔名的檔案
def get_files_with_extension(folder_path, target_extension):
    # 使用列表生成式，從指定資料夾的所有檔案中篩選出符合特定副檔名的檔案名稱
    matching_files = [filename for filename in os.listdir(folder_path) if filename.endswith(target_extension)]
    return matching_files  # 返回找尋到的符合副檔名的檔案名稱列表


# 更新播放列表中的當前播放歌曲的樣式
def update_song_list_style():
    for i in range(songs_list.size()):
        if i == index:  # 該索引值歌曲為正在播放之歌曲
            songs_list.itemconfig(i, {'bg': '#00497f', 'fg': 'white'})  # 將當前播放歌曲的背景設為藍色，前景設為白色
        else:
            songs_list.itemconfig(i, {'bg': 'black', 'fg': 'white'})  # 恢復其他歌曲的默認樣式


# 定義一個函數，用於更新音樂清單中的歌曲列表
def updatesongs():
    # 呼叫全域變數以便在函數中使用
    global index_count, song_list_mode, index

    # 清空歌曲清單視窗，刪除所有歌曲名稱
    songs_list.delete(0, tk.END)

    mypath = "D:/音樂"  # 指定音樂資料夾的路徑
    extension = ".mp3"  # 目標副檔名

    # 使用之前定義的 get_files_with_extension 函數，獲取指定資料夾中符合目標副檔名的檔案名稱列表
    matching_files = get_files_with_extension(mypath, extension)

    # 將找尋到的檔案名稱列表按照檔案的修改日期進行遞減排序
    sorted_files = sorted(matching_files, key=lambda filename: os.path.getmtime(os.path.join(mypath, filename)), reverse=True)

    if song_list_mode == 0:  # 如果播放清單模式為 0 (從新到舊)
        [songs_list.insert(END, s) for s in sorted_files]  # 將排序後的歌曲依序插入歌曲清單視窗的末尾
    if song_list_mode == 1:  # 如果播放清單模式為 1 (從舊到新)
        [songs_list.insert(0, s) for s in sorted_files]  # 將排序後的歌曲依序插入歌曲清單視窗的開頭

    index_count = songs_list.size()  # 更新歌曲總數的全域變數，以反映最新的歌曲清單
    song_index_label.config(text=("0/"+str(index_count)))  # 更新顯示目前歌曲索引的標籤文本，格式為 "目前索引/總歌曲數量"

    if mixer.music.get_busy():  # 如果播放器正在播放音樂
        songs_list.see(index)  # 將選中的歌曲移至可見區域
        song_index_label.config(text=(str(index+1)+"/"+str(index_count)))  # 更新顯示目前歌曲索引的標籤文本，格式為 "目前索引/總歌曲數量"
        update_song_list_style()  # 更新歌曲清單的樣式

# 定義一個函數，用於從音樂清單中刪除選定的歌曲
def deletesong():
    global index_count, index, song  # 呼叫全域變數以便在函數中使用

    curr_song = songs_list.curselection()  # 取得目前選中的歌曲索引

    if curr_song:  # 檢查是否有歌曲被選中
        if curr_song[0]<index:  # 如果刪除歌曲在目前播放索引值前
            index -= 1  # 索引值
            songs_list.delete(curr_song[0])  # 從歌曲清單中刪除選中的歌曲
            index_count = songs_list.size()  # 更新歌曲數量計數
            song_index_label.config(text=(str(index + 1) + "/" + str(index_count)))  # 更新歌曲索引標籤文字，顯示目前歌曲在歌曲清單中的位置
        elif curr_song[0]>index:  # 如果刪除歌曲在目前播放索引值
            songs_list.delete(curr_song[0])  # 從歌曲清單中刪除選中的歌曲
            index_count = songs_list.size()  # 更新歌曲數量計數
            song_index_label.config(text=(str(index + 1) + "/" + str(index_count)))  # 更新歌曲索引標籤文字，顯示目前歌曲在歌曲清單中的位置
        
# 定義一個函數，用於將總秒數轉換成 分鐘:秒 的格式
def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)  # 將總秒數轉換為分鐘和剩餘秒數
    return f"{int(minutes):02}:{int(seconds):02}"  # 格式化後返回 分鐘:秒 的字符串
    
# 定義一個函數，用於播放音樂，根據不同的播放類型執行不同的操作
def Play(play_type):  # play_type=1=按Play按鈕、play_type2=按Next按鈕 play_type3=按Previous按鈕 play_type4=重複播放且沒按按鈕
    global index, song_duration, song, index_count, random_bool, replay_bool  # 定義全域變數
    if play_type == 4:  # 重複播放且沒按按鈕
        song = songs_list.get(index)
    elif replay_bool == True:  # 重複播放且有按按鈕
        if play_type == 1:  # 如果播放類型為 1，表示按下播放按鈕
            index = int(songs_list.curselection()[0])  # 獲取選中的歌曲索引
            song = songs_list.get(ACTIVE)  # 獲取選中的歌曲名稱
        elif play_type == 2:
            if index + 1 == songs_list.size():  # 如果目前是最後一首歌曲
                index = 0  # 將索引設為 0，切換到第一首歌曲
            else:
                index += 1  # 否則索引增加，切換到下一首歌曲
            song = songs_list.get(index)  # 獲取下一首歌曲的名稱
        elif play_type == 3:
            if index == 0:  # 如果目前是第一首歌曲
                index = songs_list.size() - 1  # 將索引設為最後一首歌曲的索引，切換到最後一首歌曲
            else:
                index -= 1  # 否則索引減少，切換到上一首歌曲
            song = songs_list.get(index)  # 獲取上一首歌曲的名稱
    elif random_bool == True:  # 隨機播放
        if play_type == 1:  # 如果播放類型為 1，表示按下播放按鈕
            index = int(songs_list.curselection()[0])  # 獲取選中的歌曲索引
            song = songs_list.get(ACTIVE)  # 獲取選中的歌曲名稱
        elif play_type == 2:
            index = random.randint(0, index_count)  # 隨機選擇一個索引
            song = songs_list.get(index)  # 獲取對應索引的歌曲名稱
        elif play_type == 3:
            index -= 1  # 隨機模式下，總是切換到上一首歌曲
            song = songs_list.get(index)  # 獲取對應索引的歌曲名稱
    else:  # 循序播放
        if play_type == 1:  # 如果播放類型為 1，表示按下播放按鈕
            index = int(songs_list.curselection()[0])  # 獲取選中的歌曲索引
            song = songs_list.get(index)  # 獲取選中的歌曲名稱
        elif play_type == 2:  # 如果播放類型為 2，表示按下下一首按鈕
            if index + 1 == songs_list.size():  # 如果目前是最後一首歌曲
                index = 0  # 將索引設為 0，切換到第一首歌曲
            else:
                index += 1  # 否則索引增加，切換到下一首歌曲
            song = songs_list.get(index)  # 獲取下一首歌曲的名稱
        elif play_type == 3:  # 如果播放類型為 3，表示按下上一首按鈕
            if index == 0:  # 如果目前是第一首歌曲
                index = songs_list.size() - 1  # 將索引設為最後一首歌曲的索引，切換到最後一首歌曲
            else:
                index -= 1  # 否則索引減少，切換到上一首歌曲
            song = songs_list.get(index)  # 獲取上一首歌曲的名稱

    song = f'D:音樂/{song}'  # 設定歌曲的完整路徑
    mixer.music.load(song)  # 載入選中的歌曲
    remaining_time_label.config(text=f"{format_time(0)}")  # 更新顯示的剩餘播放時間
    mixer.music.play()  # 播放歌曲
    update_progress()  # 開始更新進度條
    time_label(int(MP3(song).info.length))  # 設定歌曲總長度
    progress_bar["maximum"] = int(MP3(song).info.length) * 1000  # 設置進度條的最大值
    song_duration = 0  # 重置歌曲播放時間
    nowplaying(songs_list.get(index))  # 顯示正在播放的歌曲名稱
    songs_list.see(index)  # 將選中的歌曲移至可見區域
    song_index_label.config(text=(str(index+1)+"/"+str(index_count)))  # 更新顯示目前歌曲索引的標籤文本，格式為 "目前索引/總歌曲數量"
    check_event()  # 啟動自動跳下一首歌的檢查
    update_song_list_style()  # 改變歌曲清單中正在播放歌曲的底色和文字顏色
    songs_list.selection_clear(0, tk.END)  # 清除歌曲選中狀態
    songs_list.activate(tk.END)  # 清除歌曲選中狀態底線
    play_button.config(state="disabled", bg="gray", cursor="X_cursor")  # 禁用播放按鈕
    Resume_button.config(state="disabled", bg="gray", cursor="X_cursor")  # 禁用恢復播放按鈕
    pause_button.config(state="normal", bg="white", cursor="arrow")  # 啟用暫停按鈕
    previous_button.config(state="normal", bg="white", cursor="arrow")  # 啟用上一首按鈕
    next_button.config(state="normal", bg="white", cursor="arrow")  # 啟用下一首按鈕

# 定義一個函數，用於更新進度條的顯示，顯示當前音樂播放的進度
def update_progress():
    current_position = mixer.music.get_pos()  # 獲取當前音樂的播放位置（毫秒）
    progress_bar["value"] = current_position  # 更新進度條的顯示位置
    if mixer.music.get_busy():  # 如果音樂正在播放
        root.after(1000, update_progress)  # 每隔 1000 毫秒（1 秒）後，重新呼叫該函數更新進度條

# 定義一個函數，用於更新顯示歌曲的時間標籤
time_label_id = None  # 預設無計時器
def time_label(song_length):
    global song_duration, song, time_label_id  # 宣告使用全域變數 song_duration, song, time_label_id
    total_time_label.config(text = f"{format_time(song_length)}")  # 更新顯示的總播放時間
    if mixer.music.get_busy():  # 如果音樂正在播放
        if time_label_id is not None:
            root.after_cancel(time_label_id)  # 如果之前已經有計時器在運行，則取消計時器
        time_label_id = root.after(1000, time_label, song_length)  # 建立新的計時器，每隔 1000 毫秒（1 秒）更新時間標籤
        song_duration += 1  # 增加歌曲播放時間計數
    remaining_time_label.config(text = f"{format_time(song_duration)}")  # 更新顯示的剩餘播放時間

# 定義一個函數，用於檢查音樂播放結束事件，並在音樂播放完畢時自動切換到下一首歌曲
def check_event():
    MUSIC_END = pygame.USEREVENT + 1  # 自定義事件代碼，表示音樂播放結束
    pygame.mixer.music.set_endevent(MUSIC_END)  # 設置音樂播放結束事件
    for event in pygame.event.get():  # 獲取所有的事件
        if event.type == MUSIC_END:  # 如果事件是音樂播放結束
            if replay_bool == False:  # 如果重複播放為關
                Play(2)  # 呼叫 Play 函數，播放下一首歌曲
            elif replay_bool == True:  # 如果重複播放為開
                Play(4) 
    root.after(500, check_event)  # 每隔 500 毫秒重新呼叫該函數，以持續監聽事件

# 定義一個函數，用於暫停音樂播放
def Pause():
    mixer.music.pause()  # 暫停音樂播放
    time_label(int(MP3(song).info.length))  # 更新顯示的播放時間標籤
    Resume_button.config(state="normal", bg="white", cursor="arrow")
    pause_button.config(state="disabled", bg="gray", cursor="X_cursor")

# 定義一個函數，用於恢復音樂播放
def Resume():
    mixer.music.unpause()  # 恢復音樂播放
    update_progress()  # 更新進度條的顯示
    time_label(int(MP3(song).info.length))  # 更新顯示的播放時間標籤
    Resume_button.config(state="disabled", bg="gray", cursor="X_cursor")
    pause_button.config(state="normal", bg="white", cursor="arrow")

# 定義一個函數，用於顯示目前正在播放的歌曲名稱
def nowplaying(k):
    k = str(k)  # 將歌曲名稱轉換為字串格式
    print(k)  # 輸出處理後的歌曲名稱
    label4.config(text=k[:-4])  # 將處理後的歌曲名稱設定為 Label 的內容

# 定義一個函數，用於切換按鈕的顏色（隨機播放按鈕）
def toggle_color1():
    global random_bool  # 宣告使用全域變數 random_bool
    if random_button["bg"] == "white":  # 如果按鈕背景色為白色
        random_button["bg"] = "#00FF00"  # 將按鈕背景色設為亮綠色
        random_bool = True  # 設定隨機播放為 True
        replay_button.config(state="disabled", bg="gray", cursor="X_cursor")
    else:
        random_button["bg"] = "white"  # 否則將按鈕背景色恢復為白色
        random_bool = False  # 設定隨機播放為 False
        replay_button.config(state="normal", bg="white", cursor="arrow")

# 定義一個函數，用於切換按鈕的顏色（重複播放按鈕）
def toggle_color2():
    global replay_bool  # 宣告使用全域變數 replay_bool
    if replay_button["bg"] == "white":  # 如果按鈕背景色為白色
        replay_button["bg"] = "#00FF00"  # 將按鈕背景色設為亮綠色
        replay_bool = True  # 設定重複播放為 True
        random_button.config(state="disabled", bg="gray", cursor="X_cursor")
    else:
        replay_button["bg"] = "white"  # 否則將按鈕背景色恢復為白色
        replay_bool = False  # 設定重複播放為 False
        random_button.config(state="normal", bg="white", cursor="arrow")

# 定義一個函數，用於調整音量
def update_volume(val):
    volume = float(val) / 100  # 將滑桿值轉換為 0.0 到 1.0 的音量範圍
    mixer.music.set_volume(volume)  # 設定音樂播放的音量為轉換後的值
    volume_integer = int(volume * 100)  # 將音量範圍轉換為整數百分比
    volume_value.config(text=volume_integer)  # 更新顯示音量數值的標籤

# 定義一個函數，用於切換播放清單的顯示模式
def toggle_song_list_mode():
    global index
    items = list(songs_list.get(0, "end"))
    items = items[::-1]
    songs_list.delete(0, "end")
    [songs_list.insert("end", item) for item in items]
    index = songs_list.size() - (index + 1 )
    song_index_label.config(text=(str(index+1)+"/"+str(songs_list.size()))) 
    if mixer.music.get_busy():
        songs_list.see(index)
    else:
        songs_list.see(0)
    update_song_list_style()

def update_play_button_state(event):
    selected_song = songs_list.get(songs_list.curselection())
    if selected_song:
        play_button.config(state="normal", bg="white", cursor="arrow")
    else:
        play_button.config(state="disabled", bg="gray", cursor="X_cursor")

def search(event):
    search_songs_list.delete(0,"end")
    search_filename=[]
    keyword = search_entry.get().lower()
    for item in songs_list.get(0, tk.END):  # 使用 songs_list.get() 取得所有歌曲（字符串）清單
        if keyword in item.lower():
            search_filename.append(item)
    [search_songs_list.insert("end", s) for s in search_filename]
    songs_list.grid_forget()
    search_songs_list.grid(row=2, column=0, rowspan=5, sticky="s")
    search_entry.delete(0, "end")

def search_selected(event):
    global index
    songs_list.selection_clear(0, tk.END) 
    search_song_name=search_songs_list.get(search_songs_list.curselection())
    index = songs_list.get(0, "end").index(search_song_name)
    print(index)
    search_songs_list.grid_forget()
    songs_list.grid(row=2, column=0, rowspan=5, sticky="s")
    songs_list.select_set(index)
    songs_list.see(index)
    play_button.config(state="normal", bg="white", cursor="arrow")

def open_song_list_manager_window():
    root2 = tk.Toplevel(root)
    root2.title("播放清單管理")
    root2.geometry("900x540")
    root2.resizable(False, False)
    label = tk.Label(root2, text="This is a new window!")
    label.pack()


# 建立主視窗與音樂播放器應用程式
root = Tk()  # 創建一個 Tkinter 主視窗物件
root.title('Music Player')  # 設定主視窗標題為 'Music Player'
root.geometry("900x540")  # 設定主視窗的初始尺寸為 900x540 像素
root.resizable(False, False)  # 禁止調整主視窗大小
root.configure(bg='black')  # 設定主視窗背景色為黑色
icon_image = tk.PhotoImage(file="C:\\Users\\jerem\\Desktop\\music.png")
root.iconphoto(True, icon_image)

# 初始化 Pygame，這是用於音樂播放的模組
pygame.init()
pygame.mixer.init(48000, 32, 2, 2048)

# 建立歌曲列表的標籤
label1 = Label(root, text="歌曲列表", bg='black', fg='white', font=('華康手札體W7 18 bold'))
label1.grid(row=0, column=0)  # 在主視窗中的第一列、第一欄放置標籤

# 建立可選擇歌曲的清單方塊
songs_list = Listbox(root, selectmode=SINGLE, bg="black", fg="white", font=('芫荽 0.94', 14), height=9, width=25, selectborderwidth=5)
songs_list.grid(row=2, column=0, rowspan=5, sticky="s")  # 在主視窗中的第二列、第一欄放置清單方塊，佔用五列
songs_list.bind("<ButtonRelease-1>", update_play_button_state)

# 建立可選擇歌曲的搜尋結果清單方塊
search_songs_list = Listbox(root, selectmode=SINGLE, bg="black", fg="yellow", font=('芫荽 0.94', 14), height=9, width=25, selectborderwidth=5)
search_songs_list.grid(row=2, column=0, rowspan=5, sticky="s")  # 在主視窗中的第二列、第一欄放置清單方塊，佔用五列
search_songs_list.bind("<Double-Button-1>", search_selected)
search_songs_list.grid_forget()

# 建立隨機播放按鈕
random_button = Button(root, text="🔀", bg="white", width=2, height=1, padx=0, pady=0, activebackground="gray", command=toggle_color1)
random_button['font'] = ('新細明體', 17)
random_button.grid(row=0, column=6)  # 在主視窗中的第一列、第五欄放置按鈕

# 建立重複播放按鈕
replay_button = Button(root, text="🔂", bg="white", width=2, height=1, padx=0, pady=0, activebackground="gray", command=toggle_color2)
replay_button['font'] = ('新細明體', 17)
replay_button.grid(row=0, column=2)  # 在主視窗中的第一列、第二欄放置按鈕

# 建立調整播放清單模式的按鈕
toggle_song_list_button = Button(root, text="↑", bg="white", width=2, height=1, padx=0, pady=0, activebackground="gray", command=toggle_song_list_mode)
toggle_song_list_button['font'] = ('新細明體', 17)
toggle_song_list_button.grid(row=0, column=0, sticky="e")  # 在主視窗中的第一列、第一欄放置按鈕

# 建立播放清單管理的按鈕
manage_song_list_button = Button(root, text="📂", bg="white", width=2, height=1, padx=0, pady=0, activebackground="gray", command=open_song_list_manager_window)
manage_song_list_button['font'] = ('新細明體', 17)
manage_song_list_button.grid(row=2, column=2)  # 在主視窗中的第一列、第一欄放置按鈕

# 建立重新整理歌曲清單按鈕
update_button = Button(root, text="🔄", bg="white", width=2, height=1, padx=0, pady=0, activebackground="gray", command=updatesongs)
update_button['font'] = ('新細明體', 17)
update_button.grid(row=0, column=0, sticky="w")  # 在主視窗中的第一列、第一欄放置按鈕

# 建立播放按鈕
play_button = Button(root, text="Play", width=7, activebackground="gray", command=lambda: Play(1))
play_button['font'] = ('微軟正黑體', 9)
play_button.grid(row=6, column=2, sticky="s")  # 在主視窗中的第五列、第一欄放置按鈕，粘附在底部
play_button.config(state="disabled", bg="gray", cursor="X_cursor")

# 建立暫停按鈕
pause_button = Button(root, text="Pause", width=7, activebackground="gray", command=Pause)
pause_button['font'] = ('微軟正黑體', 9)
pause_button.grid(row=6, column=3, sticky="s")  # 在主視窗中的第五列、第二欄放置按鈕，粘附在底部
pause_button.config(state="disabled", bg="gray", cursor="X_cursor")

# 建立恢復播放按鈕
Resume_button = Button(root, text="Resume", width=7, activebackground="gray", command=Resume)
Resume_button['font'] = ('微軟正黑體', 9)
Resume_button.grid(row=6, column=4, sticky="s")  # 在主視窗中的第五列、第三欄放置按鈕，粘附在底部
Resume_button.config(state="disabled", bg="gray", cursor="X_cursor")

# 建立上一首按鈕
previous_button = Button(root, text="Previous", width=7, activebackground="gray", command=lambda: Play(3))
previous_button['font'] = ('微軟正黑體', 9)
previous_button.grid(row=6, column=5, sticky="s")  # 在主視窗中的第五列、第四欄放置按鈕，粘附在底部
previous_button.config(state="disabled", bg="gray", cursor="X_cursor")

# 建立下一首按鈕
next_button = Button(root, text="Next", width=7, activebackground="gray", command=lambda: Play(2))
next_button['font'] = ('微軟正黑體', 9)
next_button.grid(row=6, column=6, sticky="s")  # 在主視窗中的第五列、第五欄放置按鈕，粘附在底部
next_button.config(state="disabled", bg="gray", cursor="X_cursor")

# 建立「現在播放」的標籤
label2 = Label(root, text="現在播放", bg='black', fg='white', font=('華康手札體W7 18 bold'))
label2.grid(row=0, column=2, columnspan=6)  # 在主視窗中的第一列、從第一欄開始，橫跨六個欄位

# 建立顯示封面圖片的標籤
photo = PhotoImage(file="C:\\Users\\jerem\\Desktop\\music.png")
label3 = Label(image=photo, width=200, height=200, bg='black')
label3.grid(row=1, column=2, columnspan=6, rowspan=5, sticky="n")  # 在主視窗中的第二列、從第一欄開始，橫跨六個欄位

# 建立顯示歌曲名稱的標籤
label4 = Label(root, text="", bg='black', fg='white', font=('芫荽 0.94', 14), justify=LEFT, wraplength=400)
label4.grid(row=4, column=2, columnspan=6)  # 在主視窗中的第三列、從第一欄開始，橫跨六個欄位

# 建立播放進度條
progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=230)
progress_bar.grid(row=5, column=3, columnspan=3)  # 在主視窗中的第五列，從第二欄開始，橫跨三個欄位

# 建立主選單
my_menu = Menu(root)
root.config(menu=my_menu)

# 在主選單中建立子選單
add_song_menu = Menu(my_menu)
my_menu.add_cascade(label="Menu", menu=add_song_menu)

# 在子選單中加入「更新歌曲」的選項，連結到更新歌曲的函式
add_song_menu.add_command(label="Update songs", command=updatesongs)

# 在子選單中加入「刪除歌曲」的選項，連結到刪除歌曲的函式
add_song_menu.add_command(label="Delete song", command=deletesong)

# 建立顯示總時間的標籤
total_time_label = Label(root, text="00:00", bg='black', fg='white', font=('芫荽 0.94', 12))
total_time_label.grid(row=5, column=6)  # 在主視窗中的第五列、第五欄放置標籤

# 建立顯示剩餘時間的標籤
remaining_time_label = Label(root, text="00:00", bg='black', fg='white', font=('芫荽 0.94', 12))
remaining_time_label.grid(row=5, column=2)  # 在主視窗中的第五列、第一欄放置標籤

# 建立顯示音量數值標籤
volume_value = Label(root, text="50", bg='black', fg='white', font=('芫荽 0.94', 12))
volume_value.grid(row=1, column=6, sticky="s")  # 在主視窗中的第二列、第五欄放置標籤

# 建立音量滑桿
volume_slider = ttk.Scale(root, from_=100, to=0, orient="vertical", length=150, command=update_volume)
volume_slider.set(50)  # 設定初始值
volume_slider.grid(row=2, column=6)  # 在主視窗中的第二列、第五欄放置音量滑桿

# 建立顯示播放曲目索引值標籤
song_index_label = Label(root, text="", bg='black', fg='white', font=('芫荽 0.94', 12))
song_index_label.grid(row=2, column=2, columnspan=2, sticky="sw")  # 放置在主視窗的第二列、第三欄，靠頂部粘附

# 建立分隔標籤
dividing_line = Label(root, text="  ", bg='black', fg='white', font=('芫荽 0.94', 10))
dividing_line.grid(row=0, column=1, rowspan=5)  # 放置在主視窗的第一列、第二欄，佔用五列空間

# 創建輸入框和搜尋按鈕
search_entry = tk.Entry(root, font=("芫荽 0.94", 12), width=27)
search_button = tk.Button(root, text="🔍", command=search)
search_button['font'] = ('新細明體', 12)
search_entry.grid(row=1, column=0, sticky="nw")
search_button.grid(row=1, column=0, sticky="ne")
search_entry.bind("<Return>", search)

# 設定全域變數初始值
song_list_mode = 0  # 播放清單排序模式  0=從新到舊  1=從舊到新
index = -1  # 選中的歌曲索引
song_duration = 0  # 歌曲播放秒數
song = ""  # 選中的歌曲名稱
index_count = 0  # 總歌曲數量
random_bool = False  # 隨機播放模式
replay_bool = False  # 重複播放模式

# 更新歌曲列表
updatesongs()

# 啟動主視窗的事件迴圈
mainloop()
import pygame
from pygame.locals import *
import random
import pygame.mixer
import pickle
from abc import ABC, abstractmethod


pygame.init()

# Buat jendela permainan
lebar = 500
tinggi = 700
ukuran_layar = (lebar, tinggi)
layar = pygame.display.set_mode(ukuran_layar)
pygame.display.set_caption('Nitro Itera Racing')

# Abstraksi
class AbstractColor(ABC):
    @abstractmethod
    # Polymorphism
    def generate_color(self):
        pass

# Kelas untuk warna hitam
class Hitam(AbstractColor):
    def generate_color(self):
        return (0, 0, 0)

# Kelas untuk warna abu-abu
class Abu(AbstractColor):
    def generate_color(self):
        return (100, 100, 100)

# Kelas untuk warna hijau
class Hijau(AbstractColor):
    def generate_color(self):
        return (76, 208, 56)

# Kelas untuk warna merah
class Merah(AbstractColor):
    def generate_color(self):
        return (200, 0, 0)

# Kelas untuk warna putih
class Putih(AbstractColor):
    def generate_color(self):
        return (255, 255, 255)

# Kelas untuk warna kuning
class Kuning(AbstractColor):
    def generate_color(self):
        return (255, 232, 0)

# Kelas untuk warna biru
class Biru(AbstractColor):
    def generate_color(self):
        return (173, 216, 230)
    
# Pengaturan warna
# Polimorpisme
hitam = Hitam().generate_color()
abu = Abu().generate_color()
hijau = Hijau().generate_color()
merah = Merah().generate_color()
putih = Putih().generate_color()
kuning = Kuning().generate_color()
biru = Biru().generate_color()

# Ukuran jalan dan marka
lebar_jalan = 300
lebar_marka = 10
tinggi_marka = 50

# Koordinat jalur
jalur_kiri = 150
jalur_tengah = 250
jalur_kanan = 350
jalur = [jalur_kiri, jalur_tengah, jalur_kanan]

# Jalan dan marka pinggir
jalan = (100, 0, lebar_jalan, tinggi)

# Untuk animasi pergerakan marka jalur
pergerakan_marka_y = 0

# Untuk mengontrol pergerakan marka dan pohon saat di-pause
pergerakan_marka_diizinkan = True
pergerakan_pohon_diizinkan = True

# Koordinat awal mobil pemain
posisi_mobil_x = 250
posisi_mobil_y = 400

# Pengaturan frame
jam = pygame.time.Clock()
fps = 120

# Pengaturan permainan
gameover = False
kecepatan = 2
skor = 0
game_paused = False

# Penanganan Kesalahan
# Inisialisasi high score
high_score = 0
try:
    with open('high_score.dat', 'rb') as file:
        high_score = pickle.load(file)
except FileNotFoundError:
    high_score = 0

# Load suara pada tampilan awal
suara_tampilan_awal = pygame.mixer.Sound('Nitro Itera Racing/Tubes/sounds/soundawal.wav')
suara_tampilan_awal.set_volume(0.5)  # Set volume suara tampilan awal

# Tambahkan variabel untuk menyimpan statuss suara tampilan awal
suara_tampilan_awal_berjalan = True

# Load suara crash
suara_crash = pygame.mixer.Sound('Nitro Itera Racing/Tubes/sounds/crash.wav')
suara_crash.set_volume(0.5) #Volume suara crash

# Tambahkan variabel untuk menyimpan status suara mobil
suara_mobil_berjalan = False

# Tambahkan variabel untuk menyimpan status suara permainan
suara_permainan_berjalan = True

# Kelas Kendaraan
class Kendaraan_rintangan(pygame.sprite.Sprite):
    def __init__(self, gambar, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Skalakan gambar agar tidak lebih lebar dari jalur
        skala_gambar = 45 / gambar.get_rect().width
        lebar_baru = gambar.get_rect().width * skala_gambar
        tinggi_baru = gambar.get_rect().height * skala_gambar
        self.image = pygame.transform.scale(gambar, (lebar_baru, tinggi_baru))

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

# Kelas Mobil Pemain dan rintangan / Pewarisan
class MobilPemain(Kendaraan_rintangan):
    def __init__(self, x, y):
        gambar = pygame.image.load('Nitro Itera Racing/Tubes/images/mobil utama/main car.png')
        super().__init__(gambar, x, y)
        self._sound_engine = pygame.mixer.Sound('Nitro Itera Racing/Tubes/sounds/suara mobil.wav')
        self._sound_engine.set_volume(0.5) #Volume suara mobil
        # Setel status suara mobil ke True saat mobil dimulai
        global suara_mobil_berjalan
        suara_mobil_berjalan = True

# Grup sprite
grup_pemain = pygame.sprite.Group()
grup_kendaraan = pygame.sprite.Group()

# Objek gambar mobil pemain 
mobil_pemain = MobilPemain(posisi_mobil_x, posisi_mobil_y)
grup_pemain.add(mobil_pemain)

# Objek gambar kendaraan dan rintangan
nama_file_gambar = ['car1.png', 'police.png', 'car2.png', 'super_car.png', 'car3.png', 'bus.png', 'car4.png', 'batu.png', 'truck1.png', 'pickup_truck.png', 'truck2.png', 'semi_trailer.png', 'truck3.png', 'taxi.png', 'truck4.png', 'van.png', 'cone.png']
gambar_kendaraan = []
for nama_file in nama_file_gambar:
    gambar = pygame.image.load('Nitro Itera Racing/Tubes/images/KendaraanDanRintangan/'+ nama_file)
    gambar_kendaraan.append(gambar)

# Objek gambar tabrakan
tabrakan = pygame.image.load('Nitro Itera Racing/Tubes/images/crash/crash.png')
rect_tabrakan = tabrakan.get_rect()

# Objek gambar pohon
pohon = pygame.image.load('Nitro Itera Racing/Tubes/images/Objek/tree1.png')
lebar_pohon = pohon.get_rect().width
tinggi_pohon = pohon.get_rect().height

# Jumlah pohon di setiap sisi jalan
num_trees = 1

# Daftar pohon untuk setiap sisi jalan
trees_left = []
trees_right = []

# Inisialisasi pohon
for i in range(num_trees):
    # Atur posisi pohon pada sisi kiri jalan
    x_kiri = (lebar // 10) - (lebar_pohon // 2)  # Posisi x di tengah sisi kiri
    y_kiri = random.randint(0, tinggi - tinggi_pohon)  # Posisi y acak di sisi kiri
    speed_kiri = random.randint(1, 3)
    trees_left.append([x_kiri, y_kiri, speed_kiri])

    # Atur posisi pohon pada sisi kanan jalan
    x_kanan = (lebar - (lebar // 10)) - (lebar_pohon // 2)  # Posisi x di tengah sisi kanan
    y_kanan = random.randint(0, tinggi - tinggi_pohon)  # Posisi y acak di sisi kanan
    speed_kanan = random.randint(1, 3)
    trees_right.append([x_kanan, y_kanan, speed_kanan])

# Load gambar pause
gambar_pause = pygame.image.load('Nitro Itera Racing/Tubes/images/button/pause.png')
lebar_gambar_pause = 50
tinggi_gambar_pause = 690
posisi_gambar_pause = (lebar - lebar_gambar_pause - 40, tinggi - tinggi_gambar_pause - 10)

# Load gambar tombol mute
gambar_mute_on = pygame.image.load('Nitro Itera Racing/Tubes/images/button/suara on.png')
gambar_mute_off = pygame.image.load('Nitro Itera Racing/Tubes/images/button/suara off.png')
lebar_gambar_mute = 30
tinggi_gambar_mute = 690
posisi_gambar_mute = (lebar - lebar_gambar_mute - 15, tinggi - tinggi_gambar_mute - 10)

# Inisialisasi status suara
suara_aktif = True

layar_awal = True

while layar_awal:
    for event in pygame.event.get():
        #Memainkan suara pada tampilan awal
        if suara_tampilan_awal_berjalan:
            suara_tampilan_awal.play()
        if event.type == QUIT:
            layar_awal = False
            berjalan = False
             # Hentikan suara saat menutup permainan
            suara_tampilan_awal_berjalan = False
            suara_tampilan_awal.stop()
            pygame.quit()
        elif event.type == MOUSEBUTTONDOWN:
            # Check if play button is clicked
            if play_button_rect.collidepoint(event.pos):
                layar_awal = False
                # Menghentikan suara tampilan awal saat game dimulai
                suara_tampilan_awal_berjalan = False
                suara_tampilan_awal.stop()
                #Start the game music and sound effects
                mobil_pemain._sound_engine.play(-1)  # Start the car engine sound
                suara_permainan_berjalan = True  # Set the game sound flag to True
            # Check if exit button is clicked
            elif exit_button_rect.collidepoint(event.pos):
                layar_awal = False
                berjalan = False  # Menghentikan loop utama
                pygame.quit()

    # Load gambar latar belakang
    gambar_latar_belakang = pygame.image.load('Nitro Itera Racing/Tubes/images/Awal game/baground awal.png')

    # Gambar latar belakang
    layar.blit(gambar_latar_belakang, (0, 0))  # Ubah (0, 0) sesuai dengan posisi yang Anda inginkan

    # Load play button image
    play_button_image = pygame.image.load('Nitro Itera Racing/Tubes/images/Awal game/play1.png')
    play_button_rect = play_button_image.get_rect()
    play_button_rect.center = (lebar // 2, tinggi // 2 - 10)
    layar.blit(play_button_image, play_button_rect)

    # Load exit button image
    exit_button_image = pygame.image.load('Nitro Itera Racing/Tubes/images/Awal game/exit1.png')
    exit_button_rect = exit_button_image.get_rect()
    exit_button_rect.center = (lebar // 2, tinggi // 2 + 100)
    layar.blit(exit_button_image, exit_button_rect)

    pygame.display.update()

# Tambahkan variabel untuk menyimpan status suara mobil
suara_mobil_berjalan = False

# Loop permainan
berjalan = True

while berjalan:

    jam.tick(fps)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            berjalan = False

        # Polimorpisme    
        if event.type == KEYDOWN:
            if event.key == K_LEFT and mobil_pemain.rect.center[0] > jalur_kiri and not game_paused:
                mobil_pemain.rect.x -= 100
            elif event.key == K_RIGHT and mobil_pemain.rect.center[0] < jalur_kanan and not game_paused:
                mobil_pemain.rect.x += 100
            # Tambahkan kontrol untuk maju dan mundur
            elif event.key == K_UP and mobil_pemain.rect.top > 0 and not game_paused:
                mobil_pemain.rect.y -= 100
            elif event.key == K_DOWN and mobil_pemain.rect.bottom < tinggi and not game_paused:
                mobil_pemain.rect.y += 100
            # Tambahkan kondisi untuk pause
            elif event.key == K_p:
                game_paused = not game_paused
                # Hentikan suara mobil saat permainan di-pause
                if game_paused:
                    mobil_pemain._sound_engine.stop()
                    # Hentikan pergerakan marka dan pohon saat di-pause
                    pergerakan_marka_diizinkan = False
                    pergerakan_pohon_diizinkan = False
                else:
                    # Mainkan kembali suara mobil saat permainan dilanjutkan
                    mobil_pemain._sound_engine.play(-1)
                    # Izinkan pergerakan marka dan pohon saat permainan dilanjutkan
                    pergerakan_marka_diizinkan = True
                    pergerakan_pohon_diizinkan = True
                
            # Cek tabrakan setelah pergerakan
            for kendaraan in grup_kendaraan:
                if pygame.sprite.collide_rect(mobil_pemain, kendaraan):
                    gameover = True
                    # Hentikan suara mobil saat terjadi tabrakan
                    mobil_pemain._sound_engine.stop()
                    # Memainkan suara crash saat mobil sengaja menabrak kendaraan lain
                    if suara_permainan_berjalan:
                        suara_crash.play()
                    # Menentukan posisi gambar tabrakan
                    rect_tabrakan.center = [mobil_pemain.rect.center[0], mobil_pemain.rect.top]

        elif event.type == MOUSEBUTTONDOWN:
            if posisi_gambar_pause[0] <= event.pos[0] <= posisi_gambar_pause[0] + lebar_gambar_pause and \
               posisi_gambar_pause[1] <= event.pos[1] <= posisi_gambar_pause[1] + tinggi_gambar_pause:
                game_paused = not game_paused
                # Hentikan suara mobil saat permainan di-pause
                if game_paused:
                    mobil_pemain._sound_engine.stop()
                    # Hentikan pergerakan marka dan pohon saat di-pause
                    pergerakan_marka_diizinkan = False
                    pergerakan_pohon_diizinkan = False
                else:
                    # Mainkan kembali suara mobil saat permainan dilanjutkan
                    mobil_pemain._sound_engine.play(-1)
                    # Izinkan pergerakan marka dan pohon saat permainan dilanjutkan
                    pergerakan_marka_diizinkan = True
                    pergerakan_pohon_diizinkan = True

            # Cek apakah tombol mute ditekan
            elif posisi_gambar_mute[0] <= event.pos[0] <= posisi_gambar_mute[0] + lebar_gambar_mute and \
                 posisi_gambar_mute[1] <= event.pos[1] <= posisi_gambar_mute[1] + tinggi_gambar_mute:
                # Ubah status suara
                suara_aktif = not suara_aktif
                # Matikan atau aktifkan suara sesuai dengan status baru
                if suara_aktif:
                    mobil_pemain._sound_engine.set_volume(0.5)
                    suara_permainan_berjalan = True
                else:
                    mobil_pemain._sound_engine.set_volume(0)
                    suara_permainan_berjalan = False

    # Gambar rumput
    layar.fill(hijau)
    
    # Gambar pohon
    for i in range(num_trees):
        layar.blit(pohon, (trees_left[i][0], trees_left[i][1]))
        layar.blit(pohon, (trees_right[i][0], trees_right[i][1]))

    # Gambar jalan
    pygame.draw.rect(layar, abu, jalan)
    
    # Gambar marka pinggir
    marka_kiri_y = 0
    marka_kanan_y = 0
    while marka_kiri_y < tinggi:
        if marka_kiri_y % 20 < 10:  #Bergantian antara merah dan putih setiap 20 pixel
            warna_marka = merah
        else:
            warna_marka = putih
        pygame.draw.rect(layar, warna_marka, (95, marka_kiri_y, lebar_marka, 10))
        pygame.draw.rect(layar, warna_marka, (395, marka_kanan_y, lebar_marka, 10))
        marka_kiri_y += 10
        marka_kanan_y += 10
    
    # Pergerakan marka
    if pergerakan_marka_diizinkan:
        pergerakan_marka_y += kecepatan * 2
        if pergerakan_marka_y >= tinggi_marka * 2:
            pergerakan_marka_y = 0
    
    # Gambar marka jalur
    for y in range(tinggi_marka * -2, tinggi, tinggi_marka * 2):
        pygame.draw.rect(layar, putih, (jalur_kiri + 45, y + pergerakan_marka_y, lebar_marka, tinggi_marka))
        pygame.draw.rect(layar, putih, (jalur_tengah + 45, y + pergerakan_marka_y, lebar_marka, tinggi_marka))
        
    # Gambar mobil pemain
    grup_pemain.draw(layar)
    
    # Tambahkan kendaraan
    if len(grup_kendaraan) < 2:
        # Pastikan ada cukup celah antara kendaraan
        tambahkan_kendaraan = True
        for kendaraan in grup_kendaraan:
            if kendaraan.rect.top < kendaraan.rect.height * 1.5:
                tambahkan_kendaraan = False
                
        if tambahkan_kendaraan:

            # Pilih jalursecara acak
            jalur_acak = random.choice(jalur)
            
            # Pilihgambar kendaraan secara acak
            gambar = random.choice(gambar_kendaraan)
            kendaraan = Kendaraan_rintangan(gambar, jalur_acak, tinggi / -2)
            grup_kendaraan.add(kendaraan)
    
    # Update pohon
    if pergerakan_pohon_diizinkan:
        for i in range(num_trees):
            trees_left[i][1] += trees_left[i][2]
            trees_right[i][1] += trees_right[i][2]
            if trees_left[i][1] > tinggi + tinggi_pohon:
                trees_left[i][1] = -tinggi_pohon
                trees_left[i][2] = random.randint(1, 3)
            if trees_right[i][1] > tinggi + tinggi_pohon:
                trees_right[i][1] = -tinggi_pohon
                trees_right[i][2] = random.randint(1, 3)
    
    # Gerakkan kendaraan hanya jika permainan tidak di-pause
    if not game_paused:
        for kendaraan in grup_kendaraan:
            kendaraan.rect.y += kecepatan
        
            # Hilangkan kendaraan ketika mencapai batas layar
            if kendaraan.rect.top >= tinggi:
                kendaraan.kill()
                
                # Tambahkan skor
                skor += 1
                
                # Tingkatkan kecepatan permainan setelah melewati 5 kendaraan
                if skor > 0 and skor % 5 == 0:
                    kecepatan += 1
    
    # Gambar kendaraan
    grup_kendaraan.draw(layar)
    
    # Objek tampilan skor
    font_path = "Nitro Itera Racing/Tubes/font/pixel.ttf" 
    font = pygame.font.Font(font_path, 15)
    teks_skor = font.render('Skor : ' + str(skor), True, hitam)
    rect_teks_skor = teks_skor.get_rect()
    rect_teks_skor.topleft = (10, 9)

    # Objek tampilan high score
    teks_high_score = font.render('High Score : ' + str(high_score), True, hitam)
    rect_teks_high_score = teks_high_score.get_rect()
    rect_teks_high_score.topleft = (150, 9)

    # Buat latar untuk skor dan high score
    latar_skor = pygame.Surface((lebar, 40))
    latar_skor.fill(biru)

    # Gambar latar, skor, dan high score
    layar.blit(latar_skor, (0, 0))
    layar.blit(teks_skor, rect_teks_skor)
    layar.blit(teks_high_score, rect_teks_high_score)
    
    # Cek jika terjadi tabrakan
    if pygame.sprite.spritecollide(mobil_pemain, grup_kendaraan, True):
        gameover = True
        # Hentikan suara mobil saat terjadi tabrakan
        mobil_pemain._sound_engine.stop()
        # Memainkan suara crash saat mobil sengaja menabrak kendaraan lain
        if suara_permainan_berjalan:
            suara_crash.play()
        # Menentukan posisi gambar tabrakan
        rect_tabrakan.center = [mobil_pemain.rect.center[0], mobil_pemain.rect.top]

    #Tampilkan game over
    if gameover:
        layar.blit(tabrakan, rect_tabrakan)
        pygame.draw.rect(layar, merah, (0, 50, lebar, 100))
        
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        teks = font.render('Permainan berakhir. Main lagi ? (Ketik Y atau N)', True, putih)
        rect_teks = teks.get_rect()
        rect_teks.center = (lebar / 2, 100)
        layar.blit(teks, rect_teks)
    
    # Tampilkan tombol pause
    layar.blit(gambar_pause, posisi_gambar_pause)
    
    # Tampilkan tombol mute
    if suara_aktif:
        layar.blit(gambar_mute_on, posisi_gambar_mute)
    else:
        layar.blit(gambar_mute_off, posisi_gambar_mute)
    
    # Tampilkan overlay saat game di-pause
    if game_paused:
        overlay = pygame.Surface((lebar, tinggi))
        overlay.set_alpha(128)  # Set opacity 50%
        overlay.fill(hitam)
        layar.blit(overlay, (0, 0))
        font_pause = pygame.font.Font(pygame.font.get_default_font(), 30)
        teks_pause = font_pause.render('PAUSE', True, putih)
        rect_teks_pause = teks_pause.get_rect()
        rect_teks_pause.center = (lebar // 2, tinggi // 2)
        layar.blit(teks_pause, rect_teks_pause)
    
    pygame.display.update()

    # Tunggu masukan pengguna untuk main lagi atau keluar
    while gameover:
        
        jam.tick(fps)
        
        for event in pygame.event.get():
            
            if event.type == QUIT:
                gameover = False
                berjalan = False
                
            # Dapatkan masukan pengguna (y atau n)
            if event.type == KEYDOWN:
                if event.key == K_y:
                    # Reset permainan
                    gameover = False
                    kecepatan = 2
                    skor = 0
                    grup_kendaraan.empty()
                    mobil_pemain.rect.center = [posisi_mobil_x, posisi_mobil_y]
                    # Setel ulang suara mobil saat memulai kembali permainan
                    mobil_pemain._sound_engine.stop()
                    mobil_pemain._sound_engine.play(-1)
                elif event.key == K_n:
                    # Keluar dari permainan
                    gameover = False
                    berjalan = False

    # Update high score jika skor lebih tinggi
    if skor > high_score:
        high_score = skor
        with open('high_score.dat', 'wb') as file:
            pickle.dump(high_score, file)

pygame.quit()
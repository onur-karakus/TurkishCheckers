# Türk Daması Oyun Motoru ve Arayüzü

Bu proje, Python Flask ile geliştirilmiş, web tabanlı bir Türk Daması oyunudur. Proje, hem iki oyunculu (PvP) hem de yapay zekaya karşı (PvE) oyun modlarını destekler. Yapay zeka, Minimax arama algoritması ve Alfa-Beta Budaması optimizasyonunu kullanarak hamle hesaplaması yapar. Ayrıca, yapay zekanın kendini geliştirmesi için genetik algoritmalarla antrenman yapabilen bir altyapı içerir.

![Türk Daması Oyun Arayüzü](https://i.imgur.com/gY9R1sN.png)

## ✨ Özellikler

- **İki Oyun Modu:**
  - **Arkadaşınla Oyna (PvP):** Aynı bilgisayar üzerinde iki kişinin oynamasına olanak tanır.
  - **Bilgisayara Karşı Oyna (PvE):** Güçlü yapay zeka motoruna karşı yeteneklerinizi test edin.
- **Gerçek Zamanlı Motor Analizi:**
  - **Leela Chess Zero Benzeri Değerlendirme:** Pozisyonun avantajını, Beyaz'ın kazanma olasılığını gösteren bir yüzde (%) ile sunar.
  - **En İyi Hamle Görselleştirmesi:** Motorun önerdiği en iyi hamle, tahta üzerinde yeşil bir ok ile gösterilir.
  - **Varyant Analizi:** Motorun düşündüğü en iyi hamle dizilimlerini ve puanlamalarını listeler.
  - **Analizi Gizle/Göster:** İsteğe bağlı olarak analiz panelini kapatıp açma imkanı.
- **Ayarlanabilir Yapay Zeka Zorluğu:** 1'den 100'e kadar ayarlanabilen zorluk seviyesi ile yapay zekanın arama derinliği ve gücü dinamik olarak değişir.
- **Zaman Kontrolü:** PvP modu için farklı zaman temposu seçenekleri (10 dakika, 5|3, 3|2 vb.).
- **Hamle Notasyonu:** Oynanan tüm hamleler, standart cebirsel notasyonla sağ panelde listelenir.
- **Antrenman Altyapısı (`trainer.py`):**
  - Genetik algoritmalar kullanarak farklı "beyinlere" (ağırlıklara) sahip yapay zeka oyuncularını birbiriyle oynatır.
  - ELO puanlama sistemi ile oyuncuların gücünü ölçer ve en başarılı olanları evrimleştirerek daha güçlü yapay zekalar yaratır.

## 🛠️ Kullanılan Teknolojiler

- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+ Modüller)
- **Yapay Zeka:** Minimax Algoritması, Alfa-Beta Budaması

## 📂 Proje Yapısı


TurkishCheckers/
├── ai/                     # Yapay zeka ile ilgili tüm modüller
│   ├── init.py
│   ├── ai_player.py        # AI oyuncu havuzunu yönetir (oluşturma, kaydetme, yükleme)
│   ├── elo.py              # ELO puanlama hesaplamaları
│   ├── intelligence.py     # Ana AI motoru (Minimax, Alfa-Beta, Değerlendirme)
│   ├── trainer.py          # Genetik algoritma ile AI antrenman betiği
│   └── ai_pool.json        # Eğitilmiş AI'ların "beyinlerini" (ağırlıklarını) saklar
├── static/                 # Statik dosyalar (CSS, JS)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js         # Frontend oyun mantığı, UI yönetimi ve API iletişimi
├── templates/              # Flask HTML şablonları
│   ├── base.html           # Tüm sayfaların kullandığı ana iskelet şablon
│   ├── home.html           # Ana karşılama sayfası
│   ├── pve.html            # Bilgisayara Karşı oyun sayfası
│   └── pvp.html            # Arkadaşınla Oyna sayfası
├── app.py                  # Ana Flask uygulaması (Rotalar, API endpoint'leri)
├── game_logic.py           # Oyunun kurallarını, tahta durumunu yöneten ana motor
├── test_game_logic.py      # Oyun motoru için birim testleri (unittest)
├── requirements.txt        # Proje bağımlılıkları
└── README.md               # Bu dosya


## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:

1.  **Projeyi Klonlayın:**
    ```bash
    git clone <repository_url>
    cd TurkishCheckers
    ```

2.  **Sanal Ortam Oluşturun (Önerilir):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux için
    # venv\Scripts\activate    # Windows için
    ```

3.  **Bağımlılıkları Yükleyin:**
    Oluşturulan `requirements.txt` dosyasını kullanarak gerekli kütüphaneleri yükleyin.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Uygulamayı Çalıştırın:**
    ```bash
    flask run
    ```

5.  Tarayıcınızda `http://127.0.0.1:5000` adresine gidin.

## 🎮 Nasıl Oynanır?

- **Oyun Modu Seçimi:** Ana sayfadan "Bilgisayara Karşı Oyna" veya "Arkadaşınla Oyna" seçeneklerinden birini seçin.
- **Yeni Oyun Başlatma:** Sağdaki panelden istediğiniz zorluk veya zaman ayarlarını seçip "Yeni Oyuna Başla" butonuna tıklayın.
- **Hamle Yapma:** Hareket ettirmek istediğiniz taşı seçin, ardından gidebileceği geçerli karelerden birine tıklayın.
- **Analiz:** Oyun sırasında, motorun pozisyon değerlendirmesini ve en iyi hamle önerilerini sağdaki analiz panelinden takip edebilirsiniz. "Gizle/Göster" butonu ile paneli yönetebilirsiniz.

## 🧠 Yapay Zeka Antrenmanı

Yapay zeka oyuncularını evrimleştirmek ve daha güçlü hale getirmek için:

1.  Terminalde proje kök dizinindeyken aşağıdaki komutu çalıştırın:
    ```bash
    python ai/trainer.py
    ```
2.  Bu betik, `ai/ai_pool.json` dosyasındaki oyuncuları birbiriyle oynatacak, ELO puanlarını güncelleyecek ve genetik algoritma (çaprazlama ve mutasyon) ile yeni nesil, daha güçlü oyuncular yaratacaktır. Sonuçlar otomatik olarak `ai_pool.json` dosyasına kaydedilir.

## 🔮 Gelecek Geliştirmeler

- [ ] **Online Multiplayer:** Socket.IO veya WebSockets kullanarak gerçek zamanlı online oyun modu.
- [ ] **Kullanıcı Hesapları:** Oyuncuların istatistiklerini ve ELO puanlarını takip edebileceği bir sistem.
- [ ] **Daha Gelişmiş AI:** Açılış kitapları ve oyun sonu veritabanları entegrasyonu.
- [ ] **UI/UX İyileştirmeleri:** Daha fazla tema seçeneği ve ses efektleri.

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from polls.models import Poll, Option, Vote
import random

class Command(BaseCommand):
    help = 'Populates the database with realistic sample polls and votes'

    def handle(self, *args, **options):
        self.stdout.write("Örnek kullanıcılar ve anketler oluşturuluyor...")

        # Create demo users
        users_data = [
            ('ahmet_k', 'ahmet@example.com', 'Demopass123!'),
            ('selin_dev', 'selin@example.com', 'Demopass123!'),
            ('caner_99', 'caner@example.com', 'Demopass123!'),
            ('zeynep_t', 'zeynep@example.com', 'Demopass123!'),
            ('mert_tech', 'mert@example.com', 'Demopass123!'),
        ]

        created_users = []
        for uname, email, pwd in users_data:
            user, created = User.objects.get_or_create(username=uname, defaults={'email': email})
            if created:
                user.set_password(pwd)
                user.save()
            created_users.append(user)

        # Sample Polls
        sample_polls = [
            {
                'user': created_users[4],
                'question': 'Yeni bir telefon alacağım, hangisini tercih etmeliyim?',
                'description': 'Kamera performansı, pil ömrü ve uzun yıllar güncelleme desteği benim için çok önemli.',
                'category': 'teknoloji',
                'options': ['iPhone 15 Pro', 'Samsung Galaxy S24 Ultra', 'Google Pixel 8 Pro'],
                'votes_count': [14, 11, 6]
            },
            {
                'user': created_users[1],
                'question': 'Akşam film gecesi için hangi türe odaklanalım?',
                'description': 'Arkadaş grubuyla izleyeceğiz, temposu hiç düşmeyen sürükleyici bir yapım arıyoruz.',
                'category': 'dizi-film',
                'options': ['Bilim Kurgu / Gizem', 'Psikolojik Gerilim', 'Komedi / Macera', 'Klasik Suç & Dedektiflik'],
                'votes_count': [18, 15, 9, 7]
            },
            {
                'user': created_users[0],
                'question': 'Ofiste öğle yemeğinde ne söyleyelim?',
                'description': 'Hızlı gelsin ve herkesi mutlu etsin istiyoruz.',
                'category': 'yemek',
                'options': ['Gurme Burger & Patates', 'Ev Yemekleri Menüsü', 'İtalyan Pizza', 'Tavuk Döner & Ayran'],
                'votes_count': [12, 8, 16, 5]
            },
            {
                'user': created_users[3],
                'question': 'Yaz tatili için 1 haftalık rota önerisi?',
                'description': 'Deniz, doğa ve sakinlik arıyorum. Çok kalabalık olmayan rotalar önceliğim.',
                'category': 'genel',
                'options': ['Kaş & Kalkan', 'Bozburun & Datça', 'Akyaka & Gökova', 'Kabak Koyu & Kelebekler Vadisi'],
                'votes_count': [22, 19, 13, 8]
            },
            {
                'user': created_users[2],
                'question': 'Yazılıma yeni başlayan biri için ilk programlama dili ne olmalı?',
                'description': 'Mantığı kavramak, hızlı proje geliştirmek ve iş olanakları açısından kararsızım.',
                'category': 'egitim',
                'options': ['Python', 'JavaScript / TypeScript', 'Java', 'C# / .NET'],
                'votes_count': [25, 20, 7, 9]
            },
            {
                'user': created_users[4],
                'question': 'Kablosuz kulaklık seçiminde hangisi daha mantıklı?',
                'description': 'Gürültü engelleme (ANC) ve mikrofon kalitesi önceliğim.',
                'category': 'teknoloji',
                'options': ['Sony WH-1000XM5', 'AirPods Pro 2', 'Bose QuietComfort Ultra'],
                'votes_count': [16, 21, 10]
            }
        ]

        for p_data in sample_polls:
            poll, created = Poll.objects.get_or_create(
                question=p_data['question'],
                defaults={
                    'user': p_data['user'],
                    'description': p_data['description'],
                    'category': p_data['category'],
                    'is_active': True,
                }
            )

            if created:
                for idx, (opt_text, vote_cnt) in enumerate(zip(p_data['options'], p_data['votes_count']), start=1):
                    option = Option.objects.create(
                        poll=poll,
                        text=opt_text,
                        order=idx
                    )
                    # Create simulated guest votes for realistic percentages
                    for v_i in range(vote_cnt):
                        Vote.objects.create(
                            poll=poll,
                            option=option,
                            session_key=f'seed_session_{poll.id}_{option.id}_{v_i}'
                        )

        self.stdout.write(self.style.SUCCESS("Tebrikler! 6 adet gerçekçi anket ve örnek oylar Supabase veritabanına eklendi."))

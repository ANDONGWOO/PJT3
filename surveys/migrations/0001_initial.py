# Generated by Django 3.2.13 on 2022-12-02 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_age', models.CharField(choices=[('10', '10대'), ('20', '20대'), ('30', '30대'), ('40', '40대'), ('50', '50대'), ('60', '60대'), ('70', '70살 이상')], max_length=10)),
                ('career', models.CharField(choices=[('lt1', '1년 미만'), ('ge1', '1년 이상'), ('ge2', '2년 이상'), ('ge3', '3년 이상'), ('ge4', '4년 이상'), ('ge5', '5년 이상'), ('senior', '시니어')], max_length=10)),
                ('developer_type', models.CharField(choices=[('full-stack', '풀스택 개발자'), ('back-end', '백엔드 개발자'), ('front-end', '프론트엔드 개발자'), ('etc', '기타')], max_length=10)),
                ('desired_language', models.CharField(choices=[('python', 'Python'), ('c', 'C'), ('java', 'Java'), ('javascript', 'JavaScript'), ('html_css', 'HTML/CSS'), ('etc', '기타')], max_length=10)),
                ('most_using_language', models.CharField(choices=[('python', 'Python'), ('c', 'C'), ('java', 'Java'), ('javascript', 'JavaScript'), ('html_css', 'HTML/CSS'), ('etc', '기타')], max_length=10)),
                ('how_to_learn', models.CharField(choices=[('school', '학교'), ('books', '책'), ('coding_bootcamp', '코딩 부트캠프'), ('online_courses', '온라인 강의'), ('other_resourses', '기타 자료 (동영상, 블로그 등)'), ('etc', '기타')], max_length=20)),
                ('daily_learning_hours', models.CharField(choices=[('lt1', '1시간 미만'), ('ge1-lt3', '1시간 이상 3시간 미만'), ('ge3-lt5', '3시간 이상 5시간 미만'), ('ge5-lt10', '5시간 이상 10시간 미만'), ('ge10', '10시간 이상')], max_length=20)),
                ('education', models.CharField(choices=[('middle_school', '중졸 이하'), ('high_school', '고졸'), ('junior_college', '전문대 졸'), ('university', '대졸 이상')], max_length=20)),
                ('degree', models.CharField(choices=[('none', '없음'), ('associate', '전문학사'), ('bachelor', '학사'), ('master', '석사'), ('doctor', '박사')], max_length=20)),
                ('gender', models.CharField(choices=[('female', '여성'), ('male', '남성'), ('third-gender', '제3의 성')], max_length=20)),
                ('mbti', models.CharField(blank=True, choices=[('ISTJ', 'ISTJ'), ('ISFJ', 'ISFJ'), ('INFJ', 'INFJ'), ('INTJ', 'INTJ'), ('ISTP', 'ISTP'), ('ISFP', 'ISFP'), ('INFP', 'INFP'), ('INTP', 'INTP'), ('ESTJ', 'ESTJ'), ('ESFJ', 'ESFJ'), ('ENFJ', 'ENFJ'), ('ENTJ', 'ENTJ'), ('ESTP', 'ESTP'), ('ESFP', 'ESFP'), ('ENFP', 'ENFP'), ('ENTP', 'ENTP')], max_length=4)),
            ],
        ),
    ]

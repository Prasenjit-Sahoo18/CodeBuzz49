from django.core.management.base import BaseCommand
from django.db import connection, transaction
from hackIDE.models import Contest, ContestProblem

class Command(BaseCommand):
	help = "Migrate data from old hackIDE_* tables into hackIDE_* (contests and problems)."

	def handle(self, *args, **options):
		with connection.cursor() as cursor:
			# Check old tables exist
			cursor.execute("""
				SELECT name FROM sqlite_master WHERE type='table' AND name IN (
					'hackIDE_contest', 'hackIDE_contestproblem'
				)
			""")
			tables = {row[0] for row in cursor.fetchall()}
			if not {'hackIDE_contest', 'hackIDE_contestproblem'} & tables:
				self.stdout.write('No old hackIDE_* tables found. Nothing to migrate.')
				return

		self.stdout.write('Starting migration of contests and problems from old hackIDE_* tables...')

		migrated_contests = 0
		migrated_problems = 0

		with transaction.atomic():
			# Migrate contests first
			with connection.cursor() as c:
				c.execute("""
					SELECT id, title, description, start_time, end_time, is_active, created_at,
						COALESCE(first_prize, 0) as first_prize,
						COALESCE(second_prize, 0) as second_prize,
						COALESCE(third_prize, 0) as third_prize
					FROM hackIDE_contest
				""")
				rows = c.fetchall()
				for (old_id, title, description, start_time, end_time, is_active, created_at,
					first_prize, second_prize, third_prize) in rows:
					contest, created = Contest.objects.get_or_create(
						title=title,
						defaults={
							'description': description or '',
							'start_time': start_time,
							'end_time': end_time,
							'is_active': bool(is_active),
							'first_prize': first_prize or 0,
							'second_prize': second_prize or 0,
							'third_prize': third_prize or 0,
						}
					)
					if not created:
						# Update key fields if changed
						contest.description = description or contest.description
						contest.start_time = start_time or contest.start_time
						contest.end_time = end_time or contest.end_time
						contest.is_active = bool(is_active)
						contest.first_prize = first_prize or contest.first_prize
						contest.second_prize = second_prize or contest.second_prize
						contest.third_prize = third_prize or contest.third_prize
						contest.save()
					migrated_contests += 1 if created else 0

			# Map old contest IDs to new Contest objects by title
			title_to_contest = {c.title: c for c in Contest.objects.all()}

			# Migrate problems
			with connection.cursor() as c:
				c.execute("""
					SELECT id, contest_id, title, description, difficulty, time_limit, memory_limit,
						COALESCE(test_cases, '[]') as test_cases,
						COALESCE(points, 100) as points,
						COALESCE(is_premium, 0) as is_premium,
						COALESCE(boilerplate_code, '{}') as boilerplate_code,
						COALESCE(company_tag, '') as company_tag,
						COALESCE(signature_enabled, 0) as signature_enabled,
						COALESCE(signature_name, '') as signature_name,
						COALESCE(signature_params, '[]') as signature_params,
						COALESCE(signature_return, '') as signature_return
					FROM hackIDE_contestproblem
				""")
				rows = c.fetchall()
				# Build map of old contest_id to contest title to resolve FK
				with connection.cursor() as c2:
					c2.execute("SELECT id, title FROM hackIDE_contest")
					old_contest_id_to_title = {row[0]: row[1] for row in c2.fetchall()}
				for (pid, old_contest_id, title, description, difficulty, time_limit, memory_limit,
					test_cases, points, is_premium, boilerplate_code, company_tag,
					signature_enabled, signature_name, signature_params, signature_return) in rows:
					contest = None
					if old_contest_id in old_contest_id_to_title:
						contest = title_to_contest.get(old_contest_id_to_title[old_contest_id])
					problem, created = ContestProblem.objects.get_or_create(
						title=title,
						contest=contest,
						defaults={
							'description': description or '',
							'difficulty': (difficulty or 'EASY'),
							'time_limit': time_limit or 1000,
							'memory_limit': memory_limit or 256,
							'test_cases': test_cases or '[]',
							'points': points or 100,
							'is_premium': bool(is_premium),
							'boilerplate_code': boilerplate_code or '{}',
							'company_tag': company_tag or '',
							'signature_enabled': bool(signature_enabled),
							'signature_name': signature_name or '',
							'signature_params': signature_params or '[]',
							'signature_return': signature_return or '',
						}
					)
					if not created:
						problem.description = description or problem.description
						problem.difficulty = difficulty or problem.difficulty
						problem.time_limit = time_limit or problem.time_limit
						problem.memory_limit = memory_limit or problem.memory_limit
						problem.test_cases = test_cases or problem.test_cases
						problem.points = points or problem.points
						problem.is_premium = bool(is_premium)
						problem.boilerplate_code = boilerplate_code or problem.boilerplate_code
						problem.company_tag = company_tag or problem.company_tag
						problem.signature_enabled = bool(signature_enabled)
						problem.signature_name = signature_name or problem.signature_name
						problem.signature_params = signature_params or problem.signature_params
						problem.signature_return = signature_return or problem.signature_return
						problem.save()
					migrated_problems += 1 if created else 0

		self.stdout.write(self.style.SUCCESS(
			f"Migration complete. Contests created: {migrated_contests}, Problems created: {migrated_problems}"
		))

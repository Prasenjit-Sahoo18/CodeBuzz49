from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from hackIDE.models import Contest, ContestProblem
import json
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create sample coding contests for demonstration'

    def handle(self, *args, **options):
        # Create a sample contest
        contest, created = Contest.objects.get_or_create(
            title="Beginner Coding Challenge",
            defaults={
                'description': 'A beginner-friendly coding contest with easy problems. Perfect for new programmers!',
                'start_time': timezone.now(),
                'end_time': timezone.now() + timedelta(days=7),
                'is_active': True
            }
        )

        if created:
            self.stdout.write(f'Created contest: {contest.title}')
        else:
            self.stdout.write(f'Contest already exists: {contest.title}')

        # Create sample problems
        problems_data = [
            {
                'title': 'Hello World',
                'description': 'Write a program that prints "Hello, World!" to the console.',
                'difficulty': 'EASY',
                'points': 50,
                'time_limit': 1000,
                'test_cases': [
                    {'input': '', 'output': 'Hello, World!'}
                ]
            },
            {
                'title': 'Sum of Two Numbers',
                'description': 'Write a program that takes two numbers as input and prints their sum.',
                'difficulty': 'EASY',
                'points': 75,
                'time_limit': 1000,
                'test_cases': [
                    {'input': '5\n3', 'output': '8'},
                    {'input': '10\n20', 'output': '30'}
                ]
            },
            {
                'title': 'Find Maximum',
                'description': 'Write a program that finds the maximum of three numbers.',
                'difficulty': 'MEDIUM',
                'points': 100,
                'time_limit': 1000,
                'test_cases': [
                    {'input': '5\n3\n9', 'output': '9'},
                    {'input': '1\n1\n1', 'output': '1'}
                ]
            },
            {
                'title': 'Two Sum',
                'description': 'Given an array and a target, return indices of the two numbers such that they add up to target.',
                'difficulty': 'MEDIUM',
                'points': 120,
                'time_limit': 2000,
                'test_cases': [
                    {'input': '4\n2 7 11 15\n9', 'output': '0 1'},
                    {'input': '3\n3 2 4\n6', 'output': '1 2'}
                ]
            },
            {
                'title': 'DP - Longest Increasing Subsequence',
                'description': 'Compute the length of the longest strictly increasing subsequence of a given array.',
                'difficulty': 'HARD',
                'points': 200,
                'time_limit': 2000,
                'test_cases': [
                    {'input': '6\n10 9 2 5 3 7', 'output': '3'},
                    {'input': '8\n0 1 0 3 2 3 4 5', 'output': '6'}
                ]
            }
        ]

        for problem_data in problems_data:
            # Ensure test_cases stored as JSON string for TextField
            data = dict(problem_data)
            data['test_cases'] = json.dumps(problem_data['test_cases'])
            problem, created = ContestProblem.objects.get_or_create(
                contest=contest,
                title=problem_data['title'],
                defaults=data
            )
            
            if created:
                self.stdout.write(f'  Created problem: {problem.title}')
            else:
                self.stdout.write(f'  Problem already exists: {problem.title}')

        # Create another contest
        contest2, created = Contest.objects.get_or_create(
            title="Algorithm Master",
            defaults={
                'description': 'Advanced algorithmic problems for experienced programmers. Test your problem-solving skills!',
                'start_time': timezone.now() + timedelta(hours=1),
                'end_time': timezone.now() + timedelta(days=3),
                'is_active': True
            }
        )

        if created:
            self.stdout.write(f'Created contest: {contest2.title}')
            
            # Create advanced problems
            advanced_problems = [
                {
                    'title': 'Binary Search',
                    'description': 'Implement binary search to find an element in a sorted array.',
                    'difficulty': 'HARD',
                    'points': 150,
                    'time_limit': 2000,
                    'test_cases': [
                        {'input': '5\n1 3 5 7 9\n5', 'output': '2'},
                        {'input': '5\n1 3 5 7 9\n10', 'output': '-1'}
                    ]
                }
            ]
            
            for problem_data in advanced_problems:
                problem, created = ContestProblem.objects.get_or_create(
                    contest=contest2,
                    title=problem_data['title'],
                    defaults=problem_data
                )
                
                if created:
                    self.stdout.write(f'  Created problem: {problem.title}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample contests!')
        )

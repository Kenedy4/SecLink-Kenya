
#  # Method to calculate the overall grade based on subject grades
# def calculate_overall_grade(self):
#         if not self.grades:
#             return None  # No grades available

#         total_score = 0
#         for grade in self.grades:
#             total_score += self._convert_letter_to_points(grade.grade)

#         # Calculate the average score
#         average_score = total_score / len(self.grades)

#         # Convert the average score back to a letter grade
#         self.overall_grade = self._convert_points_to_letter(average_score)
#         db.session.commit()

#     # Helper method to convert letter grades to points (A = 4, B = 3, etc.)
# def _convert_letter_to_points(self, letter):
#         if letter == 'A':
#             return 4
#         elif letter == 'B':
#             return 3
#         elif letter == 'C':
#             return 2
#         elif letter == 'D':
#             return 1
#         else:
#             return 0  # For 'E'

#     # Helper method to convert points to a letter grade
#     def _convert_points_to_letter(self, points):
#         if points >= 85:
#             return 'A'
#         elif points >= 75:
#             return 'B'
#         elif points >= 65:
#             return 'C'
#         elif points >= 55:
#             return 'D'
#         else:
#             return 'E'
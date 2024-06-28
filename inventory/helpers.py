import random, string
"""
This view will create random xter
"""
def randomXters(username):
	alphs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmonpqrstuvwxyz"
	allowed_chars = "".join((alphs, string.digits, username))
	result = "".join(random.choice(allowed_chars) for _ in range(25))
	return result
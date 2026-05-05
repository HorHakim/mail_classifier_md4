# à remplir


from agent_mail import classify_mail
from mail_reader import read_mails_from_gmail
from datetime import datetime
import pandas
from tqdm import tqdm

def main(start_datetime, end_datetime):
		
		emails = read_mails_from_gmail(start_datetime, end_datetime)

		emails_id = []
		emails_urgence = []
		emails_importance = []

		for email_id, email in tqdm(enumerate(emails), total=len(emails)):
			email_classification = classify_mail(email)
			emails_id.append(email_id)
			emails_urgence.append(email_classification["urgence"])
			emails_importance.append(email_classification["importance"])

		emails_classification_df = pandas.DataFrame({"emails_id": emails_id,
							  "emails": emails,
							  "emails_urgence" : emails_urgence,
							  "emails_importance": emails_importance
							})


		emails_classification_df.to_csv(f"emails_classification_{start_datetime:%Y-%m-%d}.csv", index=False)


if __name__ == "__main__":
	main(start_datetime=datetime(2025, 11, 16, 0, 0),
        end_datetime=datetime(2025, 11, 18, 23, 59))
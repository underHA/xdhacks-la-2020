# A Sound Mood - Wellness Tracker




# Inspiration

With the ongoing COVID-19 pandemic, many people’s daily lives have been put into disarray. During such a chaotic time like this, our team believes that the most important thing that people should be mindful of is their mental health and wellness. While brainstorming, we came across the topic of music therapy and how listening to certain types of music can impact your mood and mental health. Many studies show that this is the case. For example, in one study, researchers explored how listening to  music could impact stress levels in patients who were scheduled to go into surgery. It was found that the patients who listened to music remained at a normal blood pressure and heart rate, while the patients who did not experienced hypertension throughout the operation. In addition, the patients who had listened to music reported that they were calmer and felt better during it. Knowing this, we thought that it would be a great idea to build off of and create something that could help regulate a person’s mental and physical health easily. Thus, A Sound Mood was born.

# Overview

A Sound Mood is a Discord application that uses the Spotify API to track songs and gives feedback based on the songs that users listen to. If users play songs that could harm their mood (sad songs), or songs that could decrease productivity and cause the user to be distracted (songs with aggressive themes), then the bot will alert the user. 

We chose to build our project off of Discord and Spotify because they are both services that the team enjoy using daily, however, integrating between both APIs was a brand new challenge for the team. Both services also have a wide user base and are free of charge, meaning that anyone will be able to benefit from our service.

# How it works

A Sound Mood will seamlessly integrate with your Spotify activities after you have linked Discord and Spotify together in your Discord connections. After doing so, A Sound Mood will keep track of the songs that you’re playing to alert you whenever the current song will harm your wellness based on its genre. Conversely, if you are on a streak of songs that could benefit your wellness, A Sound Mood will reward you by gamifying your wellness and updating you on your “Soundness Streak” and “Wellness Score.” Ultimately, these features will encourage users to keep listening to positive music for extended periods to improve their mental health. These features require users to allow direct messaging from the bot by going to Discord "Privacy and Safety" > Enable messages from server members. 

Our service is also capable of recommending playlists to users based on their current activities. For more documentation on how each feature works, use the ?help command on our prototype. Our working application prototype of A Sound Mood is available on our Discord server: https://discord.gg/AjbBMr2 

The team believes that it is of utmost importance to respect the privacy of the user, so we do not store their song data. Users have the option to opt-out of A Sound Mood if they wish to pause wellness tracking or request data deletion by contacting a developer.


# How we built it

The application was built in Python and interfaced between the modules Discord.py and Spotipy to integrate their respective services. All of our code is maintained on GitHub and hosted on Heroku to provide a hassle-free, low latency experience to the user. With the help of cloud storage in MongoDB Atlas, our team was able to easily collaborate using the same datasets while also opening the door for sustainable data storage and platform transferability.

Some challenges that we ran into were mainly centered around user privacy. User song choices are publicly available for anyone on Discord to see, and while some users might already do this by default, others wish to be more private about their preferences. Due to technical limitations, we were not able to resolve this issue but we hope to remedy it through future expansions of our service to other operating systems (as is discussed in What’s next).

# What we learned

- Music can affect not just a person’s mental health, but also their physical health to a great extent.
- Interdisciplinary collaborations are essential to completing tasks on time.
- Information privacy is especially important to users regarding mental health.
- Gamification is an effective method to retain engagement.

# What's next

The main function of our service is easy to scale up, allowing for expansions to other services beyond Discord such as mobile applications, desktop applications, or web applications. Going through these avenues will also open up the opportunity to access a user’s current songs from various other platforms such as Apple Music or YouTube Music with the help of system events. As we expand to these operating systems in the future, the opportunity to monetize our product through the use of in-application advertisements or feature in-app purchases will financially justify these further operations, as demonstrated by the successful monetization of Calm.com (https://www.cnbc.com/2019/02/05/calm-raises-88-million-valuing-the-meditation-app-at-1-billion.html) and Headspace (https://www.priceintelligently.com/blog/headspace-calm-pricing).

Further statistical analysis could be done on each user’s song history provided that they give us consent, allowing for a deeper understanding of the impact that individual songs will have on a person’s wellness through the use of lyric and waveform machine learning, and weighted scoring algorithms. More useful statistics will allow the user to fully immerse themselves in the quest for wellness as well as allowing us to refine recommendation systems to ease a user’s transition to more peaceful music. Additionally, we hope to gain a more in-depth understanding of the impact specific genres or lyrics can have on a user through more general research and consultations with experts.


# Technologies used

Python
GitHub
Heroku
Cloud storage
MongoDB
Discord.py
Spotipy


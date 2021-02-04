import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st

from wordcloud import WordCloud, STOPWORDS

# [deprecation]
st.set_option('deprecation.showPyplotGlobalUse', False)

# Data src
DATA_URL = ("data/tweets.csv")

# Cache prevents data to reload at each action taken in page
@st.cache(persist=True)
def load_data():
    """ Load the csv data """
    data = pd.read_csv(DATA_URL)
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data


def main():
    """ Main app code """

    # Page title and subtitle
    st.title("Sentiment Analysis of Tweets about US Airlines")
    st.markdown("""This application is a Streamlit dashboard used
                to analyze sentiments of tweets""")

    # Sidebar title and subtitle
    st.sidebar.title("Sentiment Analysis of Tweets")
    st.sidebar.markdown("""This application is a Streamlit dashboard used
                        to analyze sentiments of tweets""")

    # US Airline tweet sentiment data
    data = load_data()

    # Show a random tweet from a selected sentiment type
    st.sidebar.subheader("Show random tweet")
    random_tweet = st.sidebar.radio('Sentiment', ('positive', 'neutral', 'negative'))
    st.sidebar.markdown(data.query("airline_sentiment == @random_tweet")[["text"]].sample(n=1).iat[0, 0])

    # Number os tweets from the above selected sentiment plot
    st.sidebar.subheader("Number of tweets by sentiment")
    select = st.sidebar.selectbox('Visualization type', ['Bar plot', 'Pie chart'], key='1')
    sentiment_count = data['airline_sentiment'].value_counts()
    sentiment_count = pd.DataFrame({'Sentiment':sentiment_count.index, 'Tweets':sentiment_count.values})
    # Checkbox to show/hide the plot
    if not st.sidebar.checkbox("Hide", True):
        st.subheader("Number of tweets by sentiment")
        if select == 'Bar plot':
            fig = px.bar(sentiment_count, x='Sentiment', y='Tweets', color='Tweets', height=500)
            st.plotly_chart(fig)
        elif select == 'Pie chart':
            fig = px.pie(sentiment_count, values='Tweets', names='Sentiment')
            st.plotly_chart(fig)
        else:
            pass

    # Tweets geographic position
    st.sidebar.subheader("When and where are users tweeting from?")
    hour = st.sidebar.slider("Hour to look at", 0, 23)
    modified_data = data[data['tweet_created'].dt.hour == hour]
    # Checkbox to show/hide the map
    if not st.sidebar.checkbox("Close", True, key='1'):
        st.subheader("Tweet locations based on time of day")
        st.markdown(f'{len(modified_data)} tweets between {hour}:00 and {(hour + 1) % 24}:00')
        # Exhibit a map with the tweets location
        st.map(modified_data)
        # Checkbox to show/hide raw dataframa
        if st.sidebar.checkbox("Show raw data", False):
            st.write(modified_data)

    # Tweets for each airline
    st.sidebar.subheader("Total number of tweets for each airline")
    each_airline = st.sidebar.selectbox('Visualization type', ['Bar plot', 'Pie chart'], key='2')
    airline_sentiment_count = data.groupby('airline')['airline_sentiment'].count().sort_values(ascending=False)
    airline_sentiment_count = pd.DataFrame({'Airline':airline_sentiment_count.index, 'Tweets':airline_sentiment_count.values.flatten()})
    # Show/hide plot
    if not st.sidebar.checkbox("Close", True, key='2'):
        if each_airline == 'Bar plot':
            st.subheader("Total number of tweets for each airline")
            fig_airline = px.bar(airline_sentiment_count, x='Airline', y='Tweets', color='Tweets', height=500)
            st.plotly_chart(fig_airline)
        elif each_airline == 'Pie chart':
            st.subheader("Total number of tweets for each airline")
            fig_airline = px.pie(airline_sentiment_count, values='Tweets', names='Airline')
            st.plotly_chart(fig_airline)
        else:
            pass

    # Data from specific airline
    st.sidebar.subheader("Breakdown airline by sentiment")
    choice = st.sidebar.multiselect('Pick airlines', data['airline'].unique(), key=0)
    # Start showing when 1 or more airline is selected
    if len(choice) > 0:
        choice_data = data[data.airline.isin(choice)]
        fig_choice = px.histogram(choice_data, x='airline', y='airline_sentiment',
                                  histfunc='count', color='airline_sentiment',
                                  facet_col='airline_sentiment', 
                                  labels={'airline_sentiment':'tweets'}, height=600, 
                                  width=800)
        st.plotly_chart(fig_choice)

    # Word cloud by sentiment
    st.sidebar.header("Word Cloud")
    word_sentiment = st.sidebar.radio('Display word cloud for what sentiment?', ('positive', 'neutral', 'negative'))
    # Show/hide word cloud
    if not st.sidebar.checkbox("Close", True, key='3'):
        st.subheader(f'Word cloud for {word_sentiment} sentiment')
        # Build a dataframe with only the selected sentiment
        df = data[data['airline_sentiment'] == word_sentiment]
        # Merge all words in the dataframe into a big string
        words = ' '.join(df['text'])
        # Clean all undesired words
        processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
        wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', width=800, height=640).generate(processed_words)
        plt.imshow(wordcloud)
        # Remove steps
        plt.xticks([])
        plt.yticks([])
        st.pyplot()


if __name__ == '__main__':
    main()

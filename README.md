# Walking TourBot

*A twitter bot that follows Google directions and tweets along the way*

This bot steps through a set of directions returned from a Google Directions API call and tweets data from each step to 
twitter. For each step it posts the text for the direction as well as streeview images of the endpoint (facing north, 
south, east, and west) as well as a close zoom static map with the polyline highlighted and a futher out zoom to show 
where it is more generally. Originally I had the street view images as an animated GIF, but twitter doesn't allow those to 
be posted so I changed it to one in each corner. Would prefer to move back to animation at some point if possible.

**Dependencies**
 * [Twitter](https://dev.twitter.com/) consumer keys and access tokens
 * [python-twitter Module](https://github.com/bear/python-twitter)

**TODO**
 * Add more GIS data
 * Add weather data

#### Sample Tweet

<blockquote class="twitter-tweet" lang="en">
 <p>13. Continue onto Raymond Blvd (1.9 mi, 37m) <a href="http://t.co/KfJ0bjmLG7">pic.twitter.com/KfJ0bjmLG7</a></p>
 &mdash; Walking Tour (@WalkingTourBot) 
<a href="https://twitter.com/WalkingTourBot/statuses/459300735730319361">April 24, 2014</a>
</blockquote>
<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>

#### Sample Image
 
![Sample Image](https://pbs.twimg.com/media/Bl_DlehIgAAkfNy.jpg:large "Sample Image")

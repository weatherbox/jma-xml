const projectId = 'weatherbox-217409';
const {PubSub} = require('@google-cloud/pubsub');
const pubsub = new PubSub({ projectId });

const request = require('request');
const xml2js = require('xml2js');


const feed = 'http://www.data.jma.go.jp/developer/xml/feed/';
checkUpdated(feed + 'regular.xml');
checkUpdated(feed + 'regular_l.xml');


function checkUpdated(atomfeed) { 
  request(atomfeed, (err, res, body) => {
    var parser = new xml2js.Parser();
    parser.parseString(body, (err, feed) => {
      let count = 0;
      const entries = feed.feed.entry; //.reverse();
      for (var entry of entries){
        const id = entry.id[0];
        const title = entry.title[0];
        const xml = entry.link[0].$.href;

        const updated = new Date(entry.updated[0]);
        //if (updated < new Date('2020-06-16T00:00:00Z')) continue;

        dispatch(id, title, xml, entry);
        count++;
      }
    
      console.log('updated ' + count + ' xmls');
    });

  });
}

const topics = {
  //'地上実況図': 'jma-xml-weather-map',
  //'地上２４時間予想図': 'jma-xml-weather-map',
  ////'地上４８時間予想図': 'jma-xml-weather-map',
  '警報級の可能性（明日まで）': 'jma-xml-warning-possibility-1',
  //'警報級の可能性（明後日以降）': 'jma-xml-warning-possibility-2'
};

const updated = {};

function check(entry) {
  const author = entry.author[0].name[0];
  if (author in updated) return false;
  console.log(author, entry.updated[0]);
  updated[author] = true;
  return true;
}

function dispatch(id, title, xml, entry) {

  if (title in topics) {
    if (!check(entry)) return;
    const topic = topics[title];
    console.log(id, title, xml, '->', topic);
    publish(topic, { url: xml });
  }
}


function publish(topic, message) {
  pubsub
    .topic(topic)
    .publisher()
    .publish(Buffer.from(JSON.stringify(message)))
    .then(messageId => {
      console.log(`${topic} ${messageId} published.`);
    });
}


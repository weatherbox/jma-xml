const Datastore = require('@google-cloud/datastore');
const projectId = 'weatherbox-217409';
const datastore = new Datastore({ projectId });
const lastIdKey = datastore.key(['jma-xml-last-update', 'last-id']);

const {PubSub} = require('@google-cloud/pubsub');
const pubsub = new PubSub({ projectId });

const request = require('request');
const xml2js = require('xml2js');
const atomFeed = 'http://www.data.jma.go.jp/developer/xml/feed/extra_l.xml';
//update();
checkUpdated();


function checkUpdated() { 
  request(atomFeed, (err, res, body) => {
    var parser = new xml2js.Parser();
    parser.parseString(body, (err, feed) => {
      let count = 0;

      for (var entry of feed.feed.entry){
        const id = entry.id[0];
        const title = entry.title[0];
        const xml = entry.link[0].$.href;

        dispatch(id, title, xml);
        count++;
      }
    
      console.log('updated ' + count + ' xmls');
    });

  });
}


const topics = {
  '全般気象情報': 'jma-xml-weather-info',
  '地方気象情報': 'jma-xml-weather-info',
  '府県気象情報': 'jma-xml-weather-info',
//  '気象警報・注意報（Ｈ２７）': 'jma-xml-warning'
};

function dispatch(id, title, xml) {
  if (title in topics) {
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


const Datastore = require('@google-cloud/datastore');
const projectId = 'weatherbox-217409';
const datastore = new Datastore({ projectId });
const lastIdKey = datastore.key(['jma-xml-last-update', 'regular-last-id']);

const {PubSub} = require('@google-cloud/pubsub');
const pubsub = new PubSub({ projectId });

const request = require('request');
const xml2js = require('xml2js');
const atomFeed = 'http://www.data.jma.go.jp/developer/xml/feed/regular.xml';
const atomFeedLong = 'http://www.data.jma.go.jp/developer/xml/feed/regular_l.xml';

update();
exports.handler = (event, context) => {
	update();
};

function update() {
  const transaction = datastore.transaction();

  transaction
    .run()
    .then(() => transaction.get(lastIdKey))
    .then(res => {
      const last = res[0];
      const lastId = last.lastId;
      console.log('start', lastId);

      checkUpdated(atomFeed, lastId, function(updatedLastId) {
        if (lastId == updatedLastId){
          console.log('not updated');
          return;
        }

        console.log('updated: ' + updatedLastId);
        last.lastId = updatedLastId;
        transaction.save({
          key: lastIdKey,
          data: last
        });
        return transaction.commit();
      });
    });
}

function checkUpdated(url, lastId, done) { 
  request(url, (err, res, body) => {
    var parser = new xml2js.Parser();
    parser.parseString(body, (err, feed) => {
      let count = 0;

      for (var entry of feed.feed.entry){
        const id = entry.id[0];
        const title = entry.title[0];
        const xml = entry.link[0].$.href;
        if (id == lastId) break;

        dispatch(id, title, xml);
        count++;
      }
      console.log('updated ' + count + ' xmls');
      const newLastId = feed.feed.entry[0].id[0];

      if (count == feed.feed.entry.length) {
        checkUpdated(atomFeedLong, lastId, function() {
          done(newLastId);
        });

      } else {
        done(newLastId);
      }
    });
  });
}


const topics = {
  '地上実況図': 'jma-xml-weather-map',
  '地上２４時間予想図': 'jma-xml-weather-map',
  '地上４８時間予想図': 'jma-xml-weather-map',
  '警報級の可能性（明日まで）': 'jma-xml-warning-possibility-1',
  '警報級の可能性（明後日以降）': 'jma-xml-warning-possibility-2'
};

function dispatch(id, title, xml) {
  console.log(id, title, xml);
  if (title in topics) {
    const topic = topics[title];
    console.log('->', topic);
    publish(topic, { url: xml });
  }
}


function publish(topic, message) {
  pubsub
    .topic(topic)
    .publisher()
    .publish(Buffer.from(JSON.stringify(message)))
    .then(messageId => {
      console.log(`Message ${messageId} published.`);
    });
}


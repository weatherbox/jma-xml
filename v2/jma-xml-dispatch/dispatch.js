const Datastore = require('@google-cloud/datastore');
const projectId = 'weatherbox-217409';
const datastore = new Datastore({ projectId });
const lastIdKey = datastore.key(['jma-xml-last-update', 'last-id']);

const {PubSub} = require('@google-cloud/pubsub');
const pubsub = new PubSub({ projectId });

const request = require('request');
const xml2js = require('xml2js');
const atomFeed = 'http://www.data.jma.go.jp/developer/xml/feed/extra.xml';

update();


function update() {
  const transaction = datastore.transaction();

  transaction
    .run()
    .then(() => transaction.get(lastIdKey))
    .then(res => {
      const last = res[0];
      const lastId = last.lastId;
      console.log('start', lastId);

      checkUpdated(lastId, function(updatedLastId) {
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

function checkUpdated(lastId, done) { 
  request(atomFeed, (err, res, body) => {
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
      done(feed.feed.entry[0].id[0]);
    });

  });
}


const topics = {
  '全般気象情報': 'jma-xml-weather-info',
  '地方気象情報': 'jma-xml-weather-info',
  '府県気象情報': 'jma-xml-weather-info',
  '気象警報・注意報（Ｈ２７）': 'jma-xml-warning'
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


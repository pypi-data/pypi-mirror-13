import jps
import time
import plot
import json_utils


class AddDataSubscriber(object):
    def __init__(self, plot, topic_name, element_text):
        self._plot = plot
        self._topic_name = topic_name
        self._element_text = element_text
        self._sub = jps.Subscriber(self._topic_name, self.callback)

    def callback(self, msg):
        t = time.time()
        label_data_list = json_utils.extract_data_by_text(msg, self._element_text)
        for label, data in label_data_list:
            self._plot.add_data_with_timestamp('{0}.{1}'.format(self._topic_name, label), data, t)

    def spin_once(self):
        self._sub.spin_once()
        

def main():
    import sys
    import time
    p = plot.InteructivePlotter()
    topic_element_texts = sys.argv[1:]
    subscribers = []
    for topic_element_text in topic_element_texts:
        topic, _, label = topic_element_text.partition('.')
        sub = AddDataSubscriber(p, topic, label)
        subscribers.append(sub)
    try:
        while True:
            for sub in subscribers:
                sub.spin_once()
                p.draw()
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass

    
if __name__ == '__main__':
    main()

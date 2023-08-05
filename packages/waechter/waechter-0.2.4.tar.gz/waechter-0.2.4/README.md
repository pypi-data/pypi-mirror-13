# Waechter

**Job Scheduling Helper**

## Installing

`pip install waechter`

## Usage

See samples directory for example usage.

Simple example:

```python
import waechter.scheduler


class HelloJob1(waechter.scheduler.BaseJob):
    def __init__(self, interval=None):
        super(HelloJob1, self).__init__(interval)
        self.interval = interval if interval else 1

    @classmethod
    def work(cls):
        print('hello work 1')


if __name__ == '__main__':
    main_worker = waechter.scheduler.JobScheduler().run()
```

import tempfile, csv

import mongoengine
import numpy as np
import pandas as pd

class Signal(mongoengine.DynamicDocument):
    """
    A class to hold documents from the ``eim.signals`` collection in the Emotion in Motion database.

    See :py:class:`mongoengine.Document` for more details on how to use mongoengine documents to query the database for
    signals.
    """
    meta = {
        'collection': 'signals'
    }

    data_file = mongoengine.FileField(collection_name='signals')
    _original_signals = None


    def original_signals(self):
        """
        Retrieve the original signal data from GridFS.

        Returns
        -------
        out : :py:class:`pandas.DataFrame`
            This :py:class:`pandas.DataFrame` contains each recorded signal in
            its columns.

        Examples
        --------
        >>> import eim
        >>> eim.connect('eim', 'eim')
        >>> signal = Signal.objects(id='5410edbb08ad6ee3090e20be')[0]
        >>> data = signal.original_signals()
        >>> data.iloc[0:1]
           eda_filtered  eda_raw  eda_status      hr  hr_status  pox_raw  timestamps
        0        135.05      136           1  48.387          0        0           0
        """
        if self._original_signals is None:

            # Read the file that original_data_file references into a temp file
            # and extract lines
            with tempfile.TemporaryFile(mode='w+') as csv_file:
                csv_file.write(self.data_file.read().decode('utf-8'))
                csv_file.seek(0)

                dialect = csv.Sniffer().sniff(csv_file.read(1024))
                csv_file.seek(0)

                reader = csv.reader(csv_file, dialect)
                lines = list(reader)

            # First line should be column names
            columns = lines[0]
            out_dict = {}
            for column in columns:
                out_dict[column] = []

            # Build lists for each column
            for line in lines[1:]:
                for i, column in enumerate(columns):
                    out_dict[column].append(line[i])

            # Convert each column list to a numpy.ndarray
            for column in columns:
                column_type = str if out_dict[column][0] == 'NA' else 'float64'
                out_dict[column] = np.asarray(
                    out_dict[column], dtype=column_type
                )

            # If timestamps are present, convert them to whole second measures
            if 'timestamps' in columns:
                out_dict['timestamps'] *= 0.001

            # Return a pandas.DataFrame of the signals and cache them
            self._original_signals = pd.DataFrame(out_dict)

        return self._original_signals

class Trial(mongoengine.DynamicDocument):
    """
    A class to hold documents from the ``eim.trial`` collection in the Emotion in Motion database.

    See :py:class:`mongoengine.Document` for more details on how to use mongoengine documents to query the database for
    trials.

    Attributes
    ----------
    signals : :py:class:`mongoengine.fields.ListField` of :py:class:`Signal` instances
        A list of the signals (as :py:class:`Signal` instances) in the order in which they were recorded during
        the trial
    """
    meta = {
        'collection' : 'trials'
    }

    signals = mongoengine.ListField(mongoengine.ReferenceField(Signal))


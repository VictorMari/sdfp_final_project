import { Fragment, useState, useEffect } from 'react';
import { JsonForms } from '@jsonforms/react';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import logo from './logo.svg';
import './App.css';
import schema from './schema.json';
import uischema from './uischema.json';
import {
  materialCells,
  materialRenderers,
} from '@jsonforms/material-renderers';
import RatingControl from './RatingControl';
import ratingControlTester from './ratingControlTester';
import { makeStyles } from '@material-ui/core/styles';
import { GpsFixedTwoTone } from '@material-ui/icons';

const useStyles = makeStyles((_theme) => ({
  container: {
    padding: '1em',
    width: '100%',
  },
  title: {
    textAlign: 'center',
    padding: '0.25em',
  },
  dataContent: {
    display: 'flex',
    justifyContent: 'center',
    borderRadius: '0.25em',
    backgroundColor: '#cecece',
    marginBottom: '1rem',
  },
  resetButton: {
    margin: '0 auto',
    display: 'block',
    
  },
  demoform: {
    margin: 'auto',
    padding: '1rem',
  },
}));

const initialData = {
 
};

const renderers = [
  ...materialRenderers,
  //register custom renderers
  { tester: ratingControlTester, renderer: RatingControl },
];

const App = () => {
  const classes = useStyles();
  const [displayDataAsString, setDisplayDataAsString] = useState('');
  const [jsonformsData, setJsonformsData] = useState<any>(initialData);

  useEffect(() => {
    setDisplayDataAsString(JSON.stringify(jsonformsData, null, 2));
  }, [jsonformsData]);

  const clearData = () => {
    setJsonformsData({});
  };


  const downloadData = () => {
    console.log("Download data")
    let downloadLink = document.createElement("a");
    let formData = JSON.parse(displayDataAsString)  
    let fileTitle = formData["date"] + "meals.json" 
    downloadLink.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(displayDataAsString));
    downloadLink.setAttribute("download", fileTitle);
    downloadLink.click();
  };



  return (
    <Fragment>
      <div id="download" style={{
          position: "fixed",
          width: "100%",
          top: "3%",
        }}>
        <Button
              className={classes.resetButton}
              onClick={downloadData}
              color='primary'
              variant='contained'>
          Download Json data
        </Button>
      </div>


      

      <div className={classes.demoform}>
        <JsonForms
          schema={schema}
          uischema={uischema}
          data={jsonformsData}
          renderers={renderers}
          cells={materialCells}
          onChange={({ errors, data }) => setJsonformsData(data)}
        />
      </div>
     
    </Fragment>
  );
};

export default App;
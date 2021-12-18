import * as React from 'react';
import { Button, View, ToastAndroid } from 'react-native';
import RNPickerSelect from 'react-native-picker-select';
import DateTimePicker from '@react-native-community/datetimepicker';
var data = require("./Data")

class IrrigacaoScreen extends React.Component {

    constructor(props) {
      super(props);
      this.state = {
        showTimer:false,
        date:new Date(2021,1,1,0,0,0),
        valve:0
      }
    }

  getItems(){
    if (data.configData == undefined){
      return []
    }
    valves = data.configData.valves
    items = []
    for (i = 0; i < valves.length; i++){
      item = {label:valves[i].name, value:i}
      items.push(item)
    }
    console.log(items);
    return items;
  }

  choiseTime(){
    this.setState({showTimer:true});
  }

  onChangeTimer(v){
    if (v.type == "set"){
      dt = v.nativeEvent.timestamp;
      console.log(dt);
      hour = dt.getHours()
      if (hour < 10){
        hour = "0"+hour
      }
      minute = dt.getMinutes()
      if (minute < 10){
        minute = "0"+minute
      }

      var navigation = this.props.navigation;

      timer = hour+":"+minute+":00";
      fetch('http://'+data.IP+':8080/irrigate/'+this.state.valve+'/'+timer,{
            method:"PUT"
        })
        .then(res => res.text())
        .then(resText => JSON.parse(resText.replace(/'/g, '"')))
        .then(resJson => {
            if (resJson.status == true){
              ToastAndroid.show("Irrigação iniciada", ToastAndroid.SHORT);
              navigation.navigate("Home");
            } else {
              ToastAndroid.show("Falha ao iniciar irrigação", ToastAndroid.SHORT);
            }
        }).catch(e => console.log(e));

    }
  }

  render(){
    items = this.getItems()

    return (
      <View style={{ flex: 1, alignItems: 'center'}}>

        <RNPickerSelect
            onValueChange={(value) => {this.setState({valve:value})} }
            items={items}
        />

        <Button onPress={this.choiseTime.bind(this)} title="Irrigar"></Button>

        {this.state.showTimer &&
        <DateTimePicker
                    testID="dateTimePicker"
                    value={this.state.date}
                    mode="time"
                    is24Hour={true}
                    display="spinner"
                    onChange={this.onChangeTimer.bind(this)}
                  />
        }

      </View>
    );
  }
}

export default IrrigacaoScreen;
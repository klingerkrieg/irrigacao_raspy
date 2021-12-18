//Navegacao
import { LogBox } from 'react-native';
import {createAppContainer} from 'react-navigation';
import {createStackNavigator} from 'react-navigation-stack';

import HomeScreen from './HomeScreen';

//console.disableYellowBox = true;
LogBox.ignoreAllLogs(true);

//No final do arquivo
const MainNavigator = createStackNavigator({
  Home: {screen: HomeScreen},
});


const App = createAppContainer(MainNavigator);
export default App;

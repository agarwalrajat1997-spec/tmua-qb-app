"use client";

import { useEffect, useRef, useState } from "react";
import styles from "./good-luck-popup.module.css";

const MASCOT = "data:image/webp;base64,UklGRjYgAABXRUJQVlA4ICogAABQlgCdASrgAWgBPjEYi0OiIaESmlRcIAMEsrd+DsCI0C6m8/+NJYx0lvTd68WOa/53uHMv9n/uX7Jf2L9s/oNsD9N/BP9m/ZDp6ap84DyD9M/0f+C/wX/U/yn/////3L/0P+59iP6G/6/uBfxX+W/5j+/f4//tf4r4jvUl+7HqC/pX96/6/+x/f/5nP+X/o/7d7ov8l/nv2b+AD+v/4P/q+s77Dn7mewN/Nv8L6wH/O/b74R/2s/93+v+CD+h/4r/4ewB/9vUA6nfk161vDr7r+SnsT1AfWrQQ/jH22/Ff3f2zdh/AC/Ef5R/ZvyD4NC1voBex/zz/UfbF8g3z/m1/LeoDwU9ADygP7j/xf6H0W/Sn/m/xX+X+Qv+Yf1n/Xf3j98P8986vs+/bT2Yf2W//4z4jYGNK3oHjNKGFF8gcBYx5SEUi404UD6FMxRkPXr0rPnSeQvq9XvF/ldUZK4zc1EvA5EuipjYAF2umQK0hJyePtJObAXke/OWq1EnfIUXxuDS2ESTg5oHGo1Y8i4CVXLsXPIHdplMIueZNYUbPFbERRea80BWk6YxJa+xIcG2hHiqTrQWpmyPUR4L9ktoCF8HeYb5C9mLaEfJk9s78qzvg28enBR7cTZTwuv+Hn7ucXtj1TtYWtqEJKkXBilDoe5wnb+YbOV/bIUllOIyJQd00Ccx91usvv+5OqMNFkspx3uqO7JDHU5ZsbHHOWdM+Tp7F5EnR1BiBXJkDbweEInKh9AZVtdTBlamEIyAGlCUYdaVcb4YV/eUv3iRv5AeP5rOhOLlQNjHT07OG2RTkmXAWW7M3UMX7/j7FNJKhgYZwO6z5oTuiViUYqQ7uhvdLKO6UqcOE6b3srjNA+u7BJnlofaprUa9NMMJQYR8dY7RYkumL1IGtIlMQKzLOH//4cd2ahdVHtUFHuvbzXCYA5pRCz2e9tbVxiZ0CDyxbTk6dqCbb+FZEA4NmV30FN0P3vEopVmoMLAtZFXhD8u1GnXwhPEP5qHdwWNuixHemHuV0hzoq7/OeOOW+Kd13MlcQDrSsYz8XDpnPqAYLkN5oZduz+YfL6kjmc2XIjLhQLDztbuMS+GgYUWxB7yxk05PEesvr0OCK4vphDXbMkT8zryfsC2YJ7zh22iJlaDdATmwnRc8UyqcucY/4KXwyADSykTGbt+mTFobY22SHKfP/q1APWFeI2k3l10b2xvJ6sEEZeZpjSg5bAUQY0aE5Nwf+/OO28SnKktKHAvX9G21PsWUbRKRC3kpO3v4DKn6z1DmfGYgnfgAcBhceFus5o+ayjpWe11T2k0UqiXjblFjlEgSsnFVf51l32mNfGUgcOP5X1mAm2aj4NecQpI9Yv+dW+AqhaSPmuypo9uUaysYJcXoWy7RwV8sOnkihhzRD43KolBXCoY/ecWS5mJ9tPqA5p38zy7no86qBikhR5Q6WK9h6yFZUUMDXP3cdCGCfnhv87c2evARdxm3Ifn4X608voqr0AqxzccNNoKVPOuIsawS1ToluYZVguhZCMjSf5OeX4vQHx/U26kza8lJBhSgeb8BgBAGECSXuLbUuSykG1U7GnUEyjfGvDBBYsij2aF/XZkASsATC8LpYAAD+/nu4Mgq0NKl0SSWbR0l9duEDHvKNRarvzQmGDHWXSEGrp1ILIFXAnRkTZvzwFF8K/PDkW2alSw28Y5tEUduHdLlJBoBI7jL5p44WkT0kDHPo7lOhnI1cGuc48RQJHTxRBD/mErlyo3h7OAzcoYp0Qi3OUH3I0Rwys/TX95SRkuIfs+Kv+LTvMPJUG71RwukLHVjnjsswUoHTHWxyUMOd7CzqA8iTV9MC0RsECLEa1KQijDUFI/IpEFzgTwSyckQIh8ZtJrf+UWHdsWtt8t3t1UsPgNRD6nu2dlyA6firwgU7UhypIQqX3Oqo15CnKWwCQdG9e4VvclLzxW8GeICI1JubLEmoSG3uWDPC0TTy/0L+8VG2xjZITc+/uhsfGcBbSnvBSPLoPXxFaSvozEHCHmbRHAyOFbCvlAJvS/KwsnvOwMQ/DZmTSKTzrEtMZYmF0t09dWD+lt2PqUQUd51o8UJR+xS4pKVFgxz4rlOr/i5fwedniXdt+CvzhEyBLSOxsfDY8D+rk7548eMq1/6kRXKYJuOXLfE6sdAuV0zKA/WHeULTFcUHq9mbnWDO8lP+Guwna6KE+MHeDFmqCgXAFV9Kce2SExmtq8bMA9aQ7rCOjl3zbhj3w28WJvhDgWuB+U30LEpIefqbmgiV/+S8BgrzAt/IS6o9KTNrb9XMM7r0cLwkZ31ZeGXiIh+xsZHYuygShW5/PLUOHcti2KpIkXS2TsGk5/RLE3+T4WE8umodFGRHz/kp7SgraMPAyHw3CJ7doMLWhngeREMecp33OfFR33CipA7BnbwOiMtfm9LcGfG+eOmL5yiBgfsJ94NzEL/TFntvfRUvrZ1SxgCf3AX/Org0I//+nSlpKf3XfyHQpNx2S5ifQbFsYNEDBd0Wcna/iRQZb9bhXnnw7snLzb/kd2Gdfkua2gAQt+BeQFZFETNuGZXkMPYE1vopzaf6qgC53WuB382geZ8vrRkiZxXySOFN75WpmZo770KUgo/eJN19lVKb6ealkwlNyHNfVzeKtcCj4AB2kbkoGeCJw0TMWq6M48a491cH1x+oRlD0XrU4g5ZIOf09vyZCRtHgWDaY0Hfhy+3PEDgr1PK54XLsXKPJQbMd+Q95CE75o390Ml55soWkvYmRBTa2dzpbUVWyvTVHio5x8R9NBZSWi78vapHRen8iT+EQNk6v8Y9j8Y4ostapGfETaiKLy7aXcwMb9DUFkdaUxd/xT+A1QZWSf4Nr0dNMka2N43jzcXAo3FjnWezwx8sa0HI1PNrXwHbUZBrefB2luIy6cK5yHTHlHeVmXCotN0U5o4vP1QbVyDzkTOaidfZcWW1e6ru2Cp3Ba9rfq7hYvRwTNdrDtgxYZNCkYR9pudDrTZ94xM2K7hrOiW4ziNlmrmAS6A20ojtVu/eUMHkZ2+WOt0uEIVefuP7uY+gm1Wv4AUxGAoWT1Zs8heh28N1S6ieRaX9E3IQlyOKmqZwW1qJ5HIpaa3TnWN35Xpx8ZiqlGfDZoQrc60Aid9CRrZChFYWfUYFdLnJ83psDqpElbP8PV7/iYO60uYNzkV8YfdIe7x+Q9VagpsusgA7o9VURHjyo9a4Eu68LQG/W06ZLCnZFggOuUJwBN/CC+gpDJ8txDv76JWuidMzBWUq2++Fvw1gSnZNqApOuaFq7ubXXJNn8Dle+NPoDBeETsExf1Z6iYRyx/m3/wedxuN4UY+2QKUztBSRmlcPs+5AAdrKRZ9VQBuuymGhDvuMztEh+y4P15r6SAcq7+Q5eig6ZnPIbEgWO1dtUzgN9VpRIX/csjrnK16PhQ65KLZigUnmxQJJFK4C4yFjGnTwpHFQY+FjZkS/6xvU0hMle/LEoUuTUGQ4h8aiFoBEGmCeW+McVljdOJbF6ZxFu/2W+q9hkHRBMk7DEkDfcB3qUIBAbZofq9Xa35KqqHKLSjFJYQn2z5cA6RSCUEHB9PMDzmvuKg1Ju5tYAK87NJ9ergsUo4viAFnhSqCJnwUsV4ysGrh0wx3Sw/0Yz4Oqo6WMOsdD/PNb3Mo/AjwOUZUPd5joHxle4/ulzdAQRQIuButD57Oq5dNMgoe7n3IOhZR61VN3U7PzXbyVHB7dqUlwDxtF2wFOQdmkq+ybNDLAQnq1ZpX8n89Qrl5DvB2gj+yLJNP3RUqUSE87KTbohSV9y1q9JQsjNntaggzp78UdexaQp5PMTcGMI9HLzj1cdK3ZS0NFhw2U+mOvE88lmm0I7ATvR8HWlunbdAz/WvOUZFiIasEUIh0V/b31+zkDhbWVbaoC9mHsP7i4FJYPqNbWYsPlB3vVJJKKYJu4QLB6pUc70pUUtGACDTMFLXoZGPnxVe2hCeDJD5USu0ZQsElrheAlQzjyMnm8nFeGzvYJseECX0g+9c7Wold2A7Shar4wljmZAalXhPtRXvRse6NVuzEj5RVQpdKtw42S1vdxsJ2D0ZM1/qhCbd6G09z+zH9Ow0j9oCh9L/2j6epBPyJQPptFu2uheYPD9GR2SFuxZOU3LJYZJn8GJ/DXBai6v7vQh7aarn0Ni16JhAVZaS+hX4N0dWYxAFDhTvXgs7mkNlTrM7TGNmO1gwZYYtLKgNYeg0PExkikr1djX9uU7IfHKfr+nvivUT5ddUYioWqnoCtGUPq+dzMTeE5GRj3j+xa2FO65eFpJfJwr0VaPylzp27cCIETB6j2hkEZvoa1gFstNay4yt3upnd7sl2YEtr+qqqL91nBX/0oirSAfAru3DWfnwhNRKkBWdCiC6cmL9kKMbYRmdmuyFYrYUyBk0EDBpr/FegQ174w4tDZBMgaV+o8QhaEDXJh+moZbkDKDN4bzJPXTIUGyWbEv8SDqfI2I+mHLYD7tyO/Kd3X3QQSlozAIhFzMarYEBfF91nL/vJiVA9HoyC+X0BZRi0q5MAsLtJofBtCfEUBl1liSTS4MsOUwHSXITa1srF9odpt8YP1h1f02iGPr0aUqlBsp03uaOAWVewBlJkfi2x7bDBVx/zwpMfoAysCHVHT0HIL6kzpOLruE2aHGcrRc/i7AVtUM5hoeXOcRuJx+eyEanYjLS9eThATFaWnwrTyvb0ikEQqiPQRmooDukUXpu+Ep0MFYGxwZOhppXLIwJ0Uo5hElJqR7GAPsvKj1ED+7ve/jTaHIv+IpBnonx77nPLL63TNwzFA+ExliH7NIH7DQ5LZgezr//U6lUse3GvB7QCaUuC9IsxL8w2gurrG4o488sZ9Zso/8cgJLy250E3+NkyjHuSoM13o5x3v1t4syyGGz+h5hWEnugI7uDceJurTWN957OlbI516KKJ8LFm//rwKLhfeYqJ3Cp5BMjRXlP+4c/9hwK8yDhbhAcxnnaZAOlECyPR0hbayp+xMUXt+Ie0id+c9NwNE9alWFks6YOgdq778H0MNXo1t5aVjPbYP2EA3wM/mnyIidk5sIY4ZmSdaVlVXVbSZBjo8lf9mnRMlukJOaUMKHYAXgQZeMd1SpWH1qqQSGupIgJGgn7PyOe2vjowaRO+1fQb/hD74thtjhqNK2GJP+RdFmXIXnbj4iTAS+n22eQNHS+EA6ZNGgaBOpIq+oOa5k265qS8Hqn4FowIY613YHcpQ6YSxKGxw3YGyduLJHFhqVXzBr3wr11oRa747z/0pUpDEkHsAuPewi+36inaRtYK5ekOJUrq6n5TX/DaEIlpD0YmbEDQ3snzAWWu1/n/pMpkS+wu59i4AvktDc0PRkQ6uISi3u/5cvboXl6JunbonAs4pl2oymQ69vigWoTiimvTAhRpcstvNl6I1ds7fBy2PX0rP5secEtlY3NCKPBKhpHDZieYwy90YgbOyw61rq6i3bspzjDB+xYbnS+tsLFN7PLijADjF4OetfMLpXSXIzsT3qRDBGHcUillBKlFWfFcCMtAjj671yo6oVa2tDO9+OxkKAC8qEA3yXYbItVfKePOVFonzQN2Ywf0eTyt85JUaKGNpK/eloilH44A9QqLkEDa3JGbmUTsyxrN1rjUT8Urxos5BBHTq4dfV9QUQDOkuAeztyID33lhFarndO6fgnaNdMdCoknDZK+9Osz8muYuFBKENHTPRmoyOlce15baupfJIXUwth2ooDG/iDUh0UtBlQQktlipc0NKwnUU8J+mvaItxJickNIDl8KTHxoi1R4kcoYRuAbyjtviLSYzddW1A+O+5EjPjR5uamsS6UVf6NLrV9rUmgMZoheNnS4UOEu4iB46TzGvMuiElbZNKWUos6sGOKnpN5gCamywbn8SvPBfzH+LJQzv9j1bINy+5x0DXq5KfhaXxlsIyipxKFqgbZC58YsN+X7BpvOcrZQH9XGQ9/OWBUQlB99/Ie4yGli3xDviGsV9Ag/zakkATDY2THZsyfFaALBYJBRD75nAA3ENw99+xneF33tQL3MyUjKxcvgeTfJUVzb5uQcrXNRvcNI2vG7moLmbEpjbQ8DddoIJ1c8mJB+PV/aPd2gaoL84ZXf80VZOlrc2wNIsujD+NMFbXlpoAYy5RPCeczqcNtyxzSnZzf/GgcpvZEFmm0/0w+Y0ONMC1Nfodr6JakfR7qrJIu4O5sqJ+vSr8YjVtAAX+CWSSnfKbn5BBxdP2RWQw67wg/43AbR/eCTQlQ2F029bXBx8VqZGqukESsRvCqgeyf1PmHQhngUq7PkX8RQALDM64eYqtj4XAxQfMYHEvDwJJlfNQQSFAV7wAF7JN1+CjwZ35OVT88X9Z/4kUaHBRwTq9lE7LnSEl4rdxsr6mOJFn+b9f6rtTLF2mp0V0h5Ji0wPk8/holN8lj4jf486ngew5Slq+f5HuuDSq48QIlJ8cewxu8Amg0q6ZJlDhT3zd8nKbC8J9B2OFkeAu1AcThqRwkNDPW8ZGY/V/My7qK/T4lDm9GpR8lgvImTz+Sr0gR51/MU80FA2FuVbgJtRPMI/9cNmn0szFHXxMIwIgQGZ9DFUKMmMZA3XyvMwiKXTWyS/MekB/XVKfuSNse11sPJ7XsGeNu5cYp7Dtl9ZaKl9AlmnKxyJ9jZjN6qYbsOud/yA+CQOdMpDVnTwlKaXPjRj3mYbv2CwwLotnKhTUjmPhdcN1WUL+dAMjqZtz4XYMkEoJcj9Rk6r0CZd/CnykfLVdjlJRhUsSqL6G4AP3WDc6UyxZrUMb/JN43t77CdFydz+zDP926PWBJTiQstHrAQkwS1Bmqwedfs0Iousdk1vPox9M8/ej/2s13t3iFhv+tSFbwW+yxEAZcfAgr7Z/RmywARGkWBGnUxN+7Lf+CcM6vC0PHGF+DBWQ/5LkdLdpawpS+7gsNlTwX1xUaAwJjwIc7g20OWBj39M0TI6YpA26MQp3/t4B8Wk5owIoXZgVIw4ZwMm19MNtY93DBjYh7r5hCUxiLlcRA1Pr3yEqtkUsNckIoSWHXIINs1fpU+yMHnujk+PMri1PTwbhcS7x406b0/YjSpsbIrRthwRyo0vAxnWnMaeSIpiRYmlsWiplYN+4U6X+vPpkbgI1hm5UJUARsHoCyBzmPM5Ld+89fziwW2Q+TSVk1VHOuvVn081aJVjyjhossyzFJC27GKmRNJJ+jE8nNgkCJg5+wRGWK9/Qgwkcy03ciMtKAXILxQrpU/pecYgf0icoAc1PqZFcJALNbOb0cAUADti2Y8RYTII2R0Qym2kmFiRiQLGkTVQg30NFlaVaWJ+OYioxm9/5TfblvKTqOSCLifzDxXv3NulfUbkhgOVM/RVMAKyDUQsQ02UYG6QT4I4aIIIbMd4vbIUxrDJX0vS5yUlyvQ33TOWmG/th/vO9Gh6a9INEcBOyKrSNIOcNvJLPt9TeQuVSBc3lCjOFau3dueQFi8QhgMXLVSk749XN6n479mXxJmEDWI10lxFPEumE4PN4ySDbKZ01eL3eVPvI2Ai9JxUVdIAFpunB3dI10djDh+x3Byn7PhAMd98rtnEDgzysSZUds+mqLpGnHuDIwqoloNXKeYzgOPSmnzGr7I9GIkoAvMNv2nP04Q7WS/mkonZh9IF3ED6oIaYY9lTPjZToK4qHjgPKTKqwyYOrFAkz2b3QdDg8Nd7rfei1c3VYA/9yE0FUV/hgK3bmAcUa1LZ5ktGi28jjVY+NUq2fYvTkniro1IlcRFzIA5ZWWr4rpnXc5tC/HuQJzg0eYH04AARtdgegVermKTZV1JpbPveRS8u7yPkOMOuy7HS/PHdE+Oouy5s1rmvvzIZ9rBovXrXcnzzwbljZU55dWUgZOWdQDouUeIeIo8A5/V+1Qf9oa91scuvgh779I1BFeW4cw9l91eL34rujh2Hn+6oQDJ7L9LtyRCttr3sVumWeKGboBZ9ggPPwcU2p00JsfL3KsaWmIyyU1jo5nRgztOqldgkucA7mM3z4MWFrcuRxto2yBQqjoTrMQ8vgEf/lVHLISZc0vFulV3ainZBvrUiMMUgqfEfkfZWfkcCABM9aXGI5HQHQ/P+GeWMrg6gSztLqWceObsoqI6qH2j0j7MMRsZrZWEtdmxJVnaWryyhMsJsEpGHtRRZZ4zLwl8kxxoTqnu7yPgUHhLqAyw8fNguCwMPTOhTLb2XkyzirhNj+cDOeyM12HHsFpugo1YV/qWQbjs8X7u+V7tAi8MVx+zTeUYcuKB0HrYF07+9tvMdx7T7oTrh08euaRV/XQyWo+T8ehjmGg0k5rFyllgY9RpGFvZ1MN8gAMnEbsyq6phMPhX7lxDMuAOrurhubr5i0ujC0MdoiItnfWADD7So2UuwbFCPI8h3GGGMQOour8osVpIvblT5EBy16yE0c7sInMXoU+6MKO6AKh8PMj4G08wjNXQuYSwiswMnW3zJ5QD9Q9u74dSS0zqdAVr8DsRBvlgU/6uI1XSbO3/Jc9auhjj6X2wY9Kx3H7Q5oh2SHGBFxCXWyGJ1kb4LyZpUfOJABJl4ew5fFHm391O9/S4bukhduoBhH0b5Nk+3Wc9ZD5zrf/6uEVBXhHSB9e+eEvZVj5asPerR83zcmoj68ROahKyeqlMJ2q+cLoXwLvGFSGz1DfGSu3skPlG/QfgZm/qxD3V7exT2hxa0eNk6VIiPWMrbHODxFPAsCjN9eIWXOHlWq96icFJPH71hoc3NMPiIild549daEuNpSlUdr31rGUBuwZIxsVje/+QdeyTHKYrVfnZmsG2vhyv/ZtJMwQ0QHCwsT4yq30nsHOWym9tthQFOwrrMt0ZmZA+KF/9AJrH4sAQLIcWyoHwtGLFL+gX1zh4BWPJ+Hv+3o+UX11dDDzj46rDVsW621N0/et9QzIsf2DyEcWVqzfFblWSuGBSwuaDeVwf736FQlZ5hefhEeSaR2xy2kdOIgSpQJP+iGih11URlCMT+535jktpJiSx5uJEy1+ezCcxv/tM+peUGEvqh/ZrX7baydBhTGS1/KCd3aNPB4N1BJDOhBBbskQoXAOYWZz3pQek3BGds37itZ/tjOYw8yjxxfe/hxtTxDYRH1RRxyZ3NXAwZII+xRDinee5MirUJKTwTzzt7SB1Ra/+ansotdIV/z9fHvOamVNFykK4jlbCl8hbn9+R9hh32tz1oUYeMkQc8UBvYeWPiPBEDK7d3F7ZCCxAOT1zIWbLTcVXfwIrjY0bQFoFHOUzCXKZrxtaWJj+OTKL3vsdwzdUbEBcjTJHj52lrR1fOEkW0LANTnxlXVOVM+BRwpXpfSK8ii+/hmTaXy1nTwfKAgsyYvv4BRkSpJM+VOCTSZyf01nYwH+B9xtFgyy3y4VBwtBoc2PPL3wRrRFY3IYbg2mQ1xYNJV983MDvGB2cq6W9y78u4y7C2ADr6OVyrrBItTOvfQOebhkTIF4nJseML92xeFIlFvhDDbw4F57DBFb79pjj1SyB4kq0J382nWPde1UZJt6hm5UkoLfNwguMbSsp1bGwD/8Znock53EihP2025SQJwtyXYmsP4OYPWrsmA41bJYNVOFyxDu0A8TXa0CPrZjMF94WMfVdCAYtwdG7AOH9NSA3jWUH7kz++7JGDmdfhAjCGZuPJysq5NHg3WDkf3Y8cMpjH7eOXOE3DnYHhofKUv0WK1V4nDCPSwhGxni5E8RPjlsZeRP5+aYMvxHz84FPxaE/rWh/4vr8VKOda16zq7ye0vqCEPyWC/AG3vfaa+rjlBZSTq7Hk4cIDCs6Ul9g9hqT7NaO8Ty0T+YNmKX495YNQtnDe9PqpqWsoX2LUokBL3seb+7MdbzcegGx8oCIlpaiJJMMuCSjq/upcxG2An9e6O+g/+URMzVy7mt1+lF4VZMlhsozuhJtsSMB7NjISBQLajonaBV7Fgf9eDTCuWULua5ucHnxi6Tr3NtdKE/AAwbRGJZeY/0OzScNTF9b6OZW/zNMm7lnpT760JsIpi4jCWBvyrNwdLywkXimVsx/a6SMLHXinjsOelOVwNJ4PUJ3V4rVukAhGmqEZm10u9onmOy3wGmPQ9kMb2pU4ebfqA5eYgXJiDj06ioTktBDqPpqsnGFhPFjvqfb1Gnp8CnY1NO7cM2FSuaZ4wwoUOq4z7jh49+Tj5P7nOMTwam/SGp1+OWc8pgqpuqS1WGF6/DMzJMgpQ6eFkmwD5u3r4Nw52xDriJ2j/b9WzaZZVdnsFiVVIwa0VrnG2axWPQuuMecpu72/fATXAtbxS55OFiA6GwPvgO2BdUHJQgn6iw1cz2mCCr5+2Gj59HCn/0Bu1VbmQ+CUeMbr5en3/eu2tp0UqPwZNcGmPID54cmQeb1lBoZ1eUZYQeVZ+1oMZJ1mzv6LyV9+F78sRbJHEK0UdaAMHOPO7c3DjNXiTzYYlPyf+WqnigcTfAA8vDQkadc1m+6a40r6oMWwiCT+Ie0RoBTQZOVtJTcOcQVp1/kZsA2H3Gqc9HIKpINV+bVgh87kO7vRvHGhSE+mZb/xu5XISpbHAyiWCxokwidQB8WIRT3yofdlOGHK9WRDMgRfLSkywOBWwUyeMdIneFl7aEaYKVuImVnRt86geOzv7HiErXzDBSYHVJIS8kojZuRpYRomZNj7wU2O7226R0/u5K/ZyeAZqbYo9caiO417TrGUL0zmezOpKdqeoCqGHiRSxjuh16eJ7ezqVUQtjB350e0JgdMOITdsRRtiP2aqy6/4ND4sBv8Z9klEJGJkEpuCq0mq/miLn90fLCEX3EFet5XEqQNuNs2gbqjQLaU7By+UkYU63FhTQKsAxQkFgBX0wXjleWse2j8+QETMjWqkC38HGUk5durGh13oIwUghbT4L+/RNCeV3yPxVlbaMVCuGnJqBclQcqedwsEb7Y742Yo51eTlr8qjvn2nubPJ72ZX55r1FD2tRI2pwQ5RW3ZpDsdosaxWQAAAA==";

/** Mount only after a TMUA/ESAT dashboard has confirmed student access. */
export default function GoodLuckPopup() {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const dismissedRef = useRef(false);
  const savingRef = useRef(false);
  const [visible, setVisible] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let inFlight = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    async function check() {
      if (cancelled || inFlight || dismissedRef.current || document.visibilityState !== "visible") return;
      // Do not put an optional message on top of another modal.
      const otherModal = Array.from(document.querySelectorAll("dialog[open], [aria-modal='true']"))
        .some((modal) => modal !== dialogRef.current);
      if (otherModal) {
        timer = setTimeout(() => { void check(); }, 1500);
        return;
      }
      inFlight = true;
      let retry = true;
      try {
        const result = await fetch("/api/student/good-luck-popup", {
          method: "GET",
          credentials: "same-origin",
          cache: "no-store",
          signal: AbortSignal.timeout(15_000),
        });
        if (!result.ok) return;
        const payload = await result.json() as { show?: boolean; dismissed?: boolean };
        retry = false;
        if (!cancelled && !dismissedRef.current) {
          if (payload.dismissed === true) dismissedRef.current = true;
          setVisible(payload.show === true);
        }
      } catch {
        // An optional message must not block the dashboard during an outage.
      } finally {
        inFlight = false;
        if (retry && !cancelled && !dismissedRef.current) {
          clearTimeout(timer);
          timer = setTimeout(() => { void check(); }, 30_000);
        }
      }
    }

    function schedule() {
      clearTimeout(timer);
      if (cancelled || dismissedRef.current) return;
      // Let the dashboard settle before opening the optional message.
      timer = setTimeout(() => { void check(); }, 650);
    }

    schedule();
    window.addEventListener("focus", schedule);
    window.addEventListener("online", schedule);
    document.addEventListener("visibilitychange", schedule);
    return () => {
      cancelled = true;
      clearTimeout(timer);
      window.removeEventListener("focus", schedule);
      window.removeEventListener("online", schedule);
      document.removeEventListener("visibilitychange", schedule);
    };
  }, []);

  useEffect(() => {
    if (!visible) return;
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (!dialog.open) dialog.showModal();
    return () => { if (dialog.open) dialog.close(); };
  }, [visible]);

  async function dismiss() {
    if (savingRef.current || dismissedRef.current) return;
    savingRef.current = true;
    setSaving(true);
    setSaveError(false);
    try {
      const result = await fetch("/api/student/good-luck-popup", {
        method: "POST",
        credentials: "same-origin",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "dismiss" }),
        signal: AbortSignal.timeout(15_000),
      });
      if (!result.ok || (await result.json()).dismissed !== true) throw new Error("Dismissal not saved");
      // Only close after persistence succeeds, so a completed dismissal cannot
      // reappear on another device or after clearing browser storage.
      dismissedRef.current = true;
      setVisible(false);
    } catch {
      setSaveError(true);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  if (!visible) return null;
  return (
    <dialog
      ref={dialogRef}
      className={styles.dialog}
      aria-labelledby="good-luck-title"
      aria-describedby="good-luck-copy good-luck-note"
      data-testid="good-luck-popup"
      onCancel={(event) => { event.preventDefault(); dismiss(); }}
      aria-busy={saving}
    >
      <article className={styles.card}>
        <button className={styles.close} type="button" onClick={() => { void dismiss(); }} disabled={saving} aria-label="Close and do not show this again">
          <span aria-hidden="true">×</span>
        </button>
        <p className={styles.brand}>THRIVING SCHOLARS</p>
        <div className={styles.hero} aria-hidden="true">
          <span className={styles.halo} />
          {/* The approved mascot is bundled, so it cannot fail on an external image host. */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={MASCOT} alt="" width={183} height={137} />
          <span className={`${styles.spark} ${styles.sparkA}`}>✦</span>
          <span className={`${styles.spark} ${styles.sparkB}`}>✦</span>
        </div>
        <p className={styles.tag}>A tiny pre-exam pep talk</p>
        <h2 id="good-luck-title">Big breath.<br /><span>You’ve got this.</span></h2>
        <p className={styles.copy} id="good-luck-copy">
          <strong>All the best for your exam!</strong><br />
          Relax a little, trust your prep, and save some energy for the big day. Your brain is allowed a weekend too.
        </p>
        <p className={styles.note} id="good-luck-note">
          <strong>Be confident.</strong> Bring that “nothing to lose” mindset.<br />
          Go for it, one question at a time.
        </p>
        <button className={styles.highFive} type="button" onClick={() => { void dismiss(); }} disabled={saving} aria-label="High five! Close and do not show this again">
          <span aria-hidden="true">🙌</span>
        </button>
        {saveError && <p className={styles.error} role="alert">Couldn’t save that. Please try closing again when you’re online.</p>}
        <p className={styles.signoff}>We’re rooting for you.<br /><span>Team Thriving Scholars</span></p>
      </article>
    </dialog>
  );
}

"""This module contains a dictionary which matches country code to it's common
name. This is used in `authenticate.py` and generated by `countrylist.csv`."""

__all__ = ['code_to_country']

code_to_country = {'': 'British Antarctic Territory',
 '+1': 'United States',
 '+1-242': 'Bahamas, The',
 '+1-246': 'Barbados',
 '+1-264': 'Anguilla',
 '+1-268': 'Antigua and Barbuda',
 '+1-284': 'British Virgin Islands',
 '+1-340': 'U.S. Virgin Islands',
 '+1-345': 'Cayman Islands',
 '+1-441': 'Bermuda',
 '+1-473': 'Grenada',
 '+1-649': 'Turks and Caicos Islands',
 '+1-664': 'Montserrat',
 '+1-670': 'Northern Mariana Islands',
 '+1-671': 'Guam',
 '+1-684': 'American Samoa',
 '+1-758': 'Saint Lucia',
 '+1-767': 'Dominica',
 '+1-784': 'Saint Vincent and the Grenadines',
 '+1-787 and 1-939': 'Puerto Rico',
 '+1-809 and 1-829': 'Dominican Republic',
 '+1-868': 'Trinidad and Tobago',
 '+1-869': 'Saint Kitts and Nevis',
 '+1-876': 'Jamaica',
 '+20': 'Egypt',
 '+212': 'Western Sahara',
 '+213': 'Algeria',
 '+216': 'Tunisia',
 '+218': 'Libya',
 '+220': 'Gambia, The',
 '+221': 'Senegal',
 '+222': 'Mauritania',
 '+223': 'Mali',
 '+224': 'Guinea',
 '+225': "Cote d'Ivoire (Ivory Coast)",
 '+226': 'Burkina Faso',
 '+227': 'Niger',
 '+228': 'Togo',
 '+229': 'Benin',
 '+230': 'Mauritius',
 '+231': 'Liberia',
 '+232': 'Sierra Leone',
 '+233': 'Ghana',
 '+234': 'Nigeria',
 '+235': 'Chad',
 '+236': 'Central African Republic',
 '+237': 'Cameroon',
 '+238': 'Cape Verde',
 '+239': 'Sao Tome and Principe',
 '+240': 'Equatorial Guinea',
 '+241': 'Gabon',
 '+242': 'Congo, Republic of the (Congo \x96 Brazzaville)',
 '+243': 'Congo, Democratic Republic of the (Congo \x96 Kinshasa)',
 '+244': 'Angola',
 '+245': 'Guinea-Bissau',
 '+246': 'British Indian Ocean Territory',
 '+247': 'Ascension',
 '+248': 'Seychelles',
 '+249': 'Sudan',
 '+250': 'Rwanda',
 '+251': 'Ethiopia',
 '+252': 'Somaliland',
 '+253': 'Djibouti',
 '+254': 'Kenya',
 '+255': 'Tanzania',
 '+256': 'Uganda',
 '+257': 'Burundi',
 '+258': 'Mozambique',
 '+260': 'Zambia',
 '+261': 'Madagascar',
 '+262': 'Reunion',
 '+263': 'Zimbabwe',
 '+264': 'Namibia',
 '+265': 'Malawi',
 '+266': 'Lesotho',
 '+267': 'Botswana',
 '+268': 'Swaziland',
 '+269': 'Comoros',
 '+27': 'South Africa',
 '+290': 'Tristan da Cunha',
 '+291': 'Eritrea',
 '+297': 'Aruba',
 '+298': 'Faroe Islands',
 '+299': 'Greenland',
 '+30': 'Greece',
 '+31': 'Netherlands',
 '+32': 'Belgium',
 '+33': 'France',
 '+34': 'Spain',
 '+350': 'Gibraltar',
 '+351': 'Portugal',
 '+352': 'Luxembourg',
 '+353': 'Ireland',
 '+354': 'Iceland',
 '+355': 'Albania',
 '+356': 'Malta',
 '+357': 'British Sovereign Base Areas',
 '+358': 'Finland',
 '+358-18': 'Aland',
 '+359': 'Bulgaria',
 '+36': 'Hungary',
 '+370': 'Lithuania',
 '+371': 'Latvia',
 '+372': 'Estonia',
 '+373': 'Moldova',
 '+373-533': 'Pridnestrovie (Transnistria)',
 '+374': 'Armenia',
 '+374-97': 'Nagorno-Karabakh',
 '+375': 'Belarus',
 '+376': 'Andorra',
 '+377': 'Monaco',
 '+378': 'San Marino',
 '+379': 'Vatican City',
 '+380': 'Ukraine',
 '+381': 'Kosovo',
 '+382': 'Montenegro',
 '+385': 'Croatia',
 '+386': 'Slovenia',
 '+387': 'Bosnia and Herzegovina',
 '+389': 'Macedonia',
 '+39': 'Italy',
 '+40': 'Romania',
 '+41': 'Switzerland',
 '+420': 'Czech Republic',
 '+421': 'Slovakia',
 '+423': 'Liechtenstein',
 '+43': 'Austria',
 '+44': 'Jersey',
 '+45': 'Denmark',
 '+46': 'Sweden',
 '+47': 'Svalbard',
 '+48': 'Poland',
 '+49': 'Germany',
 '+500': 'Falkland Islands (Islas Malvinas)',
 '+501': 'Belize',
 '+502': 'Guatemala',
 '+503': 'El Salvador',
 '+504': 'Honduras',
 '+505': 'Nicaragua',
 '+506': 'Costa Rica',
 '+507': 'Panama',
 '+508': 'Saint Pierre and Miquelon',
 '+509': 'Haiti',
 '+51': 'Peru',
 '+52': 'Mexico',
 '+53': 'Cuba',
 '+54': 'Argentina',
 '+55': 'Brazil',
 '+56': 'Chile',
 '+57': 'Colombia',
 '+58': 'Venezuela',
 '+590': 'Guadeloupe',
 '+591': 'Bolivia',
 '+592': 'Guyana',
 '+593': 'Ecuador',
 '+594': 'French Guiana',
 '+595': 'Paraguay',
 '+596': 'Martinique',
 '+597': 'Suriname',
 '+598': 'Uruguay',
 '+599': 'Netherlands Antilles',
 '+60': 'Malaysia',
 '+61': 'Cocos (Keeling) Islands',
 '+62': 'Indonesia',
 '+63': 'Philippines',
 '+64': 'New Zealand',
 '+65': 'Singapore',
 '+66': 'Thailand',
 '+670': 'Timor-Leste (East Timor)',
 '+672': 'Norfolk Island',
 '+673': 'Brunei',
 '+674': 'Nauru',
 '+675': 'Papua New Guinea',
 '+676': 'Tonga',
 '+677': 'Solomon Islands',
 '+678': 'Vanuatu',
 '+679': 'Fiji',
 '+680': 'Palau',
 '+681': 'Wallis and Futuna',
 '+682': 'Cook Islands',
 '+683': 'Niue',
 '+685': 'Samoa',
 '+686': 'Kiribati',
 '+687': 'New Caledonia',
 '+688': 'Tuvalu',
 '+689': 'French Polynesia',
 '+690': 'Tokelau',
 '+691': 'Micronesia',
 '+692': 'Marshall Islands',
 '+7': 'Russia',
 '+81': 'Japan',
 '+82': 'Korea, Republic of  (South Korea)',
 '+84': 'Vietnam',
 '+850': "Korea, Democratic People's Republic of (North Korea)",
 '+852': 'Hong Kong',
 '+853': 'Macau',
 '+855': 'Cambodia',
 '+856': 'Laos',
 '+86': "China, People's Republic of",
 '+880': 'Bangladesh',
 '+886': 'China, Republic of (Taiwan)',
 '+90': 'Turkey',
 '+90-392': 'Northern Cyprus',
 '+91': 'India',
 '+92': 'Pakistan',
 '+93': 'Afghanistan',
 '+94': 'Sri Lanka',
 '+95': 'Myanmar (Burma)',
 '+960': 'Maldives',
 '+961': 'Lebanon',
 '+962': 'Jordan',
 '+963': 'Syria',
 '+964': 'Iraq',
 '+965': 'Kuwait',
 '+966': 'Saudi Arabia',
 '+967': 'Yemen',
 '+968': 'Oman',
 '+970': 'Palestinian Territories (Gaza Strip and West Bank)',
 '+971': 'United Arab Emirates',
 '+972': 'Israel',
 '+973': 'Bahrain',
 '+974': 'Qatar',
 '+975': 'Bhutan',
 '+976': 'Mongolia',
 '+977': 'Nepal',
 '+98': 'Iran',
 '+992': 'Tajikistan',
 '+993': 'Turkmenistan',
 '+994': 'Azerbaijan',
 '+995': 'South Ossetia',
 '+996': 'Kyrgyzstan',
 '+998': 'Uzbekistan'}

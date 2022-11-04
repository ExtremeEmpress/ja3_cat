# coding: utf-8
db_f = "../data/db.json"

puts "Collecting data from db"

require 'json'
require 'date'

# database: will contain o:H->P(A)
database = {}

month_hashes = {}
followed_days = {}
f = File.read(db_f)
f = f.gsub("\\,",",")
db_json = JSON.parse(f)

puts "db_size: #{db_json.size}"

print(db_json.first)


apps = []

db_json.each do |ja3fp,progs|
  progs.each do |exe|
    #puts exe[1]
    #exit
    if not apps.include? exe[0]
      apps.push exe[0]
    end
  end
end


puts "endpoint apps: #{apps.size}"
#puts apps.join("\n")


unique_ja3s = []

db_json.each do |ja3,progs|
  if database[ja3].nil?
    database[ja3] = []
  end
  unique_ja3s.push ja3 unless unique_ja3s.include?(ja3)
end

puts "unique ja3s: #{unique_ja3s.size}"
#puts "here: #{unique_ja3s.join(",")}"

app_ja3s = {}
unique_ja3s_followed = []
ja3_app = {}
ja3_app_metadata = {}
prod_ja3s = {}
cat_ja3s = {}
cat_products = {}

db_json.each do |ja3,progs|
  if not ja3_app.has_key?(ja3)
    ja3_app[ja3]={}
    ja3_app_metadata[ja3]={}
  end
  progs.each do |exe|
    #if dec_2018_apps.include? exe[0]
      product = exe[1].first[1].find{|key,value| value=="Executable Product"}[0]
      if product == "Microsoft® Windows® -käyttöjärjestelmä"
        product = "Microsoft® Windows® Operating System"
      elsif product == "Google Päivitä"
        product = "Google Update"
      elsif product =~ /^Java\(TM\) Platform SE/
        product = "Java(TM) Platform SE"
      elsif product =~ /Steam Client WebHelper/ or product =~ /Steam Client Bootstrapper/ 
        product = "Steam"
      elsif product =~ /OriginThinSetupInternal/ or product =~ /OriginWebHelperService/ or product =~ /EALink/
        product = "Origin"
      elsif product == "Firefox"
        if exe[0]=="default-browser-agent.exe" or exe[0]=="setup-stub.exe"
          product = "Microsoft® Windows® Operating System"
          category = "Windows OS"
        end
      end
      if not database[ja3].include? product
        database[ja3].push product
      end
      if product == "Microsoft® Windows® Operating System" or product =~ /LocalBridge/
        category = "Windows OS"
      elsif product == "Google Update" or product == "Java Platform SE Auto Updater"
        category = "Product Updater"
      elsif product == "Google Chrome" or product == "Microsoft Edge" or product == "Firefox" or product =~ /Microsoft Edge/
        category = "Web Browser"
      elsif product == "Steam" or product == "Origin" or product == "Spotify" or product =~ /EasyAntiCheat Launcher/ or product =~ /Minecraft/ or product =~ /Paradox Launcher/ or product =~ /STAR WARS Jedi: Fallen Order™/ or product =~ /Titanfall 2/ or product =~ /Unravel Two/
        category = "Entertainment"
      else
        category = "Other"
      end
      if not cat_products.has_key? category
        cat_products[category] = []
      end
      cat_products[category].push product
      if not app_ja3s.has_key? exe[0]
        app_ja3s[exe[0]] = {}
      end
      if not prod_ja3s.has_key? product
        prod_ja3s[product]={}
      end
      if not cat_ja3s.has_key? category
        cat_ja3s[category] = {}
      end
      if not app_ja3s[exe[0]].has_key? ja3
        app_ja3s[exe[0]][ja3] = {}
      end
      if not prod_ja3s[product].has_key? ja3
        prod_ja3s[product][ja3] = {}
      end
      if not cat_ja3s[category].has_key? ja3
        cat_ja3s[category][ja3] = {}
      end
      if not ja3_app[ja3].has_key? exe[0]
        ja3_app[ja3][exe[0]] = true
        ja3_app_metadata[ja3][exe[0]] = {}
      end
      ja3_app_metadata[ja3][exe[0]] = exe[1]
      app_ja3s[exe[0]][ja3] = exe[1]
      app_ja3s[exe[0]][ja3]["product"] = product
      app_ja3s[exe[0]][ja3]["category"] = category
      prod_ja3s[product][ja3] = exe[1]
      cat_ja3s[category][ja3] = exe[1]
      unique_ja3s_followed.push ja3 unless unique_ja3s_followed.include?(ja3)
    #end
  end
end

puts "unique ja3s: #{unique_ja3s_followed.size}"

f_ja3_uniq_only = File.open("../data/ja3_uniq_only.csv","w")
unique_ja3s_followed.each do |ja3|
  f_ja3_uniq_only.puts ja3
end
f_ja3_uniq_only.close

f_prod_ja3 = File.open("../data/prod_ja3.csv", "w")
prod_ja3s.each do |prod,ja3s|
  ja3s.each do |ja3|
    f_prod_ja3.puts "#{prod},#{ja3}"
  end
end
f_prod_ja3.close

# Print some specific products into their own files

f_ff_ja3 = File.open("../data/firefox.csv", "w")
f_c_ja3 = File.open("../data/chrome.csv", "w")
f_w_ja3 = File.open("../data/windows.csv", "w")
prod_ja3s.each do |prod,ja3s|
  if prod == "Firefox"
    ja3s.each do |ja3,meta|
      f_ff_ja3.puts ja3
    end
  elsif prod == "Google Chrome"
    ja3s.each do |ja3,meta|
      f_c_ja3.puts ja3
    end
  elsif prod == "Microsoft® Windows® Operating System"
    ja3s.each do |ja3,meta|
      f_w_ja3.puts ja3
    end
  end
end
f_ff_ja3.close
f_c_ja3.close
f_w_ja3.close

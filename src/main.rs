use std::fs::File;
use std::path::Path;
use std::io::prelude::*;
use std::{mem, slice};

use bitvec::prelude::*;
// use bitvec::view::BitViewSized;
// use byteorder::ByteOrder;
// use indicatif::ProgressBar;


fn encode(filename: String) {
    let path = Path::new("data/ig.ori");
    let display = path.display();
    let mut fi = match File::open(&path) {
        Err(why) => panic!("couldn't create {}: {}", display, why),
        Ok(file) => file,
    };
    let mut slice_u8 = Vec::new();
    match fi.read_to_end(&mut slice_u8) {
        Err(why) => panic!("couldn't read {}: {}", display, why),
        Ok(flen) => println!("read {} bytes from {}", flen, display),
    }

    let ev: &[i32] = unsafe {
        slice::from_raw_parts(
            slice_u8.as_ptr() as *const i32,
            slice_u8.len() / 4,
        )
    };

    let mut bv: BitVec<Msb0, u8> = BitVec::new();
    // let bar = ProgressBar::new(bv.len() as u64);
    for v in ev.iter() {
        // bar.inc(1);
        let mut value = *v;
        if value == 0 {
            value = 0x7FFF_FFFFi32
        }
        if value == -1 {
            value = 0x7FFF_FFFEi32
        }
        assert!(value > 0, "Elias Gamma only encodes >0 value.");
        let lzs = value.leading_zeros();
        let nbits: u32 = 32 - lzs - 1;

        // println!("nb{}", nbits);
        for _ in 0 .. nbits {
            bv.push(false);
        }
        bv.push(true);
        value = value << lzs;
        // print!("{}", data);
        for _ in 0 .. nbits {
            bv.push(value & 0x4000_0000i32 == 0x4000_0000i32);
            value = value << 1;
        }
    }
    let path = Path::new("data/ig.enc");
    let display = path.display();

    let mut file = match File::create(&path) {
        Err(why) => panic!("couldn't create {}: {}", display, why),
        Ok(file) => file,
    };
    // println!("{}", bv);
    let ve = bv.into_vec();
    match file.write_all(&ve) {
        Err(why) => panic!("couldn't write {}: {}", display, why),
        Ok(_) => println!("written bytes {}", display),
    }

}

fn decode() {
    let path = Path::new("data/ig.enc");
    let display = path.display();

    let mut file = match File::open(&path) {
        Err(why) => panic!("couldn't open {}: {}", display, why),
        Ok(file) => file,
    };

    let mut buff = Vec::new();
    match file.read_to_end(&mut buff) {
        Err(why) => panic!("couldn't read {}: {}", display, why),
        Ok(flen) => print!("{} contains: {} Bytes\n", display, flen),
    }
    let bv: BitVec<Msb0, u8> = BitVec::from_vec(buff);
    let mut ar: Vec<i32> = Vec::new();

    let mut state = 0;
    let mut bz = 0;
    let mut number: i32 = 1;
   
    for bp in bv.iter() {
        let bb = *bp;

        if state == 0 {
            if bb == false {
                bz += 1;
            }
            else {
                state = 1;
                if bz == 0 {
                    ar.push(1);
                    state = 0; 
                    number = 1;
                }
            }
            continue;
        }

        if state == 1 {
            if bz > 0 {
                bz -= 1;
                number = (number << 1) + bb as i32;
            }
            if bz == 0 {
                state = 0;
                if number == 0x7FFF_FFFFi32 {
                    number = 0;
                }
                if number == 0x7FFF_FFFEi32 {
                    number = -1;
                }
                ar.push(number);
                number = 1;
            }
        }
    }

    let path = Path::new("data/ig.dec");
    let display = path.display();
    let mut fo = match File::create(&path) {
        Err(why) => panic!("couldn't create {}: {}", display, why),
        Ok(file) => file,
    };
    // println!("{}", bv);
    // let mut buff = Vec::new();
    // byteorder::NativeEndian::write_u8(&mut buff, ar);
    let slice_u8: &[u8] = unsafe {
        slice::from_raw_parts(
            ar.as_ptr() as *const u8,
            ar.len() * mem::size_of::<u32>(),
        )
    };
    match fo.write_all(&slice_u8) {
        Err(why) => panic!("couldn't write {}: {}", display, why),
        Ok(_) => println!("written bytes"),
    }
    
}

fn main() {
    let mut filename = String::from("data/ig");
    encode(filename);
    decode();
}